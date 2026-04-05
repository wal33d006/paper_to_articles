import json

from langgraph.graph import StateGraph, END

from backend.models import PaperState
from backend.agents.extractor import extract_paper
from backend.agents.simplifier import simplify_paper
from backend.agents.writers import write_technical, write_general, write_eli5
from backend.agents.judge import judge_posts, route_after_judge


def build_pipeline():
    graph = StateGraph(PaperState)

    graph.add_node("extractor", extract_paper)
    graph.add_node("simplifier", simplify_paper)
    graph.add_node("technical_writer", write_technical)
    graph.add_node("general_writer", write_general)
    graph.add_node("eli5_writer", write_eli5)
    graph.add_node("judge", judge_posts)

    graph.set_entry_point("extractor")
    graph.add_edge("extractor", "simplifier")

    graph.add_edge("simplifier", "technical_writer")
    graph.add_edge("simplifier", "general_writer")
    graph.add_edge("simplifier", "eli5_writer")

    graph.add_edge("technical_writer", "judge")
    graph.add_edge("general_writer", "judge")
    graph.add_edge("eli5_writer", "judge")

    graph.add_conditional_edges(
        "judge",
        route_after_judge,
        {
            "end": END,
            "revise": "technical_writer"
        }
    )

    return graph.compile()


def stream_pipeline(raw_text: str):
    if not raw_text.strip():
        raise ValueError("Paper text cannot be empty.")

    pipeline = build_pipeline()
    last_state = None

    for event in pipeline.stream(
            {
                "raw_text": raw_text,
                "paper_content": None,
                "simplified": None,
                "technical_post": None,
                "general_post": None,
                "eli5_post": None,
                "verdict": None,
                "revision_count": 0
            },
            stream_mode="values"
    ):
        last_state = event

        if event.get("paper_content") and not event.get("simplified"):
            paper = event["paper_content"]
            yield f"status: Extracted paper — {paper.title}\n\n"

        elif event.get("simplified") and not event.get("technical_post"):
            yield f"status: Simplified core concepts. Starting all three writers in parallel...\n\n"

        elif event.get("technical_post") and not event.get("verdict"):
            writers_done = sum([
                bool(event.get("technical_post")),
                bool(event.get("general_post")),
                bool(event.get("eli5_post"))
            ])
            yield f"status: {writers_done} of 3 posts written...\n\n"

        elif event.get("verdict"):
            verdict = event["verdict"]
            if verdict.approved:
                yield f"status: Judge approved all posts (score: {verdict.overall_score}/10).\n\n"
            else:
                yield f"status: Judge requested revisions (score: {verdict.overall_score}/10). Revision {event['revision_count']} of 2...\n\n"

    if last_state and last_state.get("technical_post"):
        payload = json.dumps({
            "technical": {
                "title": last_state["technical_post"].title,
                "content": last_state["technical_post"].content,
                "key_takeaways": last_state["technical_post"].key_takeaways
            },
            "general": {
                "title": last_state["general_post"].title,
                "content": last_state["general_post"].content,
                "key_takeaways": last_state["general_post"].key_takeaways
            },
            "eli5": {
                "title": last_state["eli5_post"].title,
                "content": last_state["eli5_post"].content,
                "key_takeaways": last_state["eli5_post"].key_takeaways
            },
            "verdict": {
                "score": last_state["verdict"].overall_score,
                "accuracy_concerns": last_state["verdict"].accuracy_concerns
            },
            "paper_content": {
                "title": last_state["paper_content"].title,
                "findings": last_state["paper_content"].findings,
                "results": last_state["paper_content"].results,
                "conclusions": last_state["paper_content"].conclusions,
                "limitations": last_state["paper_content"].limitations,
                "keywords": last_state["paper_content"].keywords
            }
        })
        yield f"result: {payload}\n\n"
