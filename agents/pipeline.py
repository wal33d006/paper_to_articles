from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from agents.models import (
    PaperContent,
    SimplifiedContent,
    BlogPost,
    JudgeVerdict,
    PaperState
)
from agents.config import config


# ── Model ──────────────────────────────────────────────────────────────────

def get_model():
    return ChatGoogleGenerativeAI(
        model=config.model_name,
        google_api_key=config.google_api_key,
        temperature=config.temperature
    )


# ── Agent 1: Extractor ─────────────────────────────────────────────────────

def extract_paper(state: PaperState) -> dict:
    model = get_model().with_structured_output(PaperContent)

    prompt = f"""
  You are an academic research analyst.

  Read the research paper text below and extract its key components into a structured format.
  Be thorough and precise — preserve the academic accuracy of all findings and conclusions.

  Paper Text:
  {state["raw_text"]}
  """

    result = model.invoke([HumanMessage(content=prompt)])
    return {"paper_content": result}


# ── Agent 2: Simplifier ────────────────────────────────────────────────────

def simplify_paper(state: PaperState) -> dict:
    model = get_model().with_structured_output(SimplifiedContent)

    paper = state["paper_content"]

    prompt = f"""
  You are a science communicator who excels at making complex research accessible.

  Based on the research paper details below, create a simplified understanding guide
  that three different blog writers will use as their foundation.

  Title: {paper.title}
  Authors: {paper.authors}
  Abstract: {paper.abstract}
  Methodology: {paper.methodology}
  Findings: {paper.findings}
  Results: {paper.results}
  Conclusions: {paper.conclusions}
  Limitations: {paper.limitations}
  Keywords: {paper.keywords}

  Create a core insight, explain why it matters, find a real world analogy,
  and map all technical jargon to plain English.
  """

    result = model.invoke([HumanMessage(content=prompt)])
    return {"simplified": result}


# ── Agent 3a: Technical Writer ─────────────────────────────────────────────

def write_technical(state: PaperState) -> dict:
    model = get_model().with_structured_output(BlogPost)

    paper = state["paper_content"]
    simplified = state["simplified"]
    verdict = state.get("verdict")

    feedback = ""
    if verdict and not verdict.approved:
        feedback = f"""
  Previous attempt was rejected. Specific feedback for this post:
  {verdict.feedback_per_post.get("technical", "Improve accuracy and depth.")}
  Accuracy concerns to fix: {verdict.accuracy_concerns}
  """

    prompt = f"""
  You are a technical blog writer for an audience of researchers, engineers, and scientists.

  Write a detailed blog post about this research paper. Your audience understands
  technical terminology, statistics, and domain-specific concepts. Go deep on
  methodology and results. Use precise language.

  Paper Title: {paper.title}
  Authors: {paper.authors}
  Core Insight: {simplified.core_insight}
  Why It Matters: {simplified.why_it_matters}
  Methodology: {paper.methodology}
  Findings: {paper.findings}
  Results: {paper.results}
  Conclusions: {paper.conclusions}
  Limitations: {paper.limitations}
  {feedback}

  Write in markdown format. Include sections for background, methodology,
  findings, implications, and limitations.
  Set target_audience to "technical".
  """

    result = model.invoke([HumanMessage(content=prompt)])
    return {"technical_post": result}


# ── Agent 3b: General Writer ───────────────────────────────────────────────

def write_general(state: PaperState) -> dict:
    model = get_model().with_structured_output(BlogPost)

    paper = state["paper_content"]
    simplified = state["simplified"]
    verdict = state.get("verdict")

    feedback = ""
    if verdict and not verdict.approved:
        feedback = f"""
  Previous attempt was rejected. Specific feedback for this post:
  {verdict.feedback_per_post.get("general", "Make it more accessible and engaging.")}
  Accuracy concerns to fix: {verdict.accuracy_concerns}
  """

    prompt = f"""
  You are a science journalist writing for an educated general audience — think
  readers of The Atlantic or BBC Science. They are intelligent but not specialists.
  Avoid jargon. Use the analogy provided. Focus on the human story and real world impact.

  Paper Title: {paper.title}
  Core Insight: {simplified.core_insight}
  Why It Matters: {simplified.why_it_matters}
  Real World Analogy: {simplified.real_world_analogy}
  Jargon Map: {simplified.jargon_map}
  Conclusions: {paper.conclusions}
  Limitations: {paper.limitations}
  {feedback}

  Write in markdown format. Keep it engaging, accurate, and free of unexplained jargon.
  Set target_audience to "general".
  """

    result = model.invoke([HumanMessage(content=prompt)])
    return {"general_post": result}


# ── Agent 3c: ELI5 Writer ──────────────────────────────────────────────────

def write_eli5(state: PaperState) -> dict:
    model = get_model().with_structured_output(BlogPost)

    paper = state["paper_content"]
    simplified = state["simplified"]
    verdict = state.get("verdict")

    feedback = ""
    if verdict and not verdict.approved:
        feedback = f"""
  Previous attempt was rejected. Specific feedback for this post:
  {verdict.feedback_per_post.get("eli5", "Simplify further, use more analogies.")}
  Accuracy concerns to fix: {verdict.accuracy_concerns}
  """

    prompt = f"""
  You are writing for curious 10-year-olds and complete beginners with no
  scientific background. Use the simplest possible words. Use lots of analogies.
  Make it fun and exciting. Short sentences. No jargon whatsoever.
  The goal is that after reading this, a child understands what was discovered and why it is cool.

  Paper Title: {paper.title}
  Core Insight: {simplified.core_insight}
  Real World Analogy: {simplified.real_world_analogy}
  Why It Matters: {simplified.why_it_matters}
  {feedback}

  Write in markdown format. Use simple words, short paragraphs, and fun comparisons.
  Set target_audience to "eli5".
  """

    result = model.invoke([HumanMessage(content=prompt)])
    return {"eli5_post": result}


# ── Agent 4: Judge ─────────────────────────────────────────────────────────

def judge_posts(state: PaperState) -> dict:
    model = get_model().with_structured_output(JudgeVerdict)

    paper = state["paper_content"]
    technical = state["technical_post"]
    general = state["general_post"]
    eli5 = state["eli5_post"]

    prompt = f"""
  You are a rigorous editorial judge and fact-checker for a science publication.

  Your job is to review three blog posts written about a research paper and verify:
  1. Factual accuracy — do the posts correctly represent the paper's findings?
  2. No hallucinations — did any writer invent claims not in the original paper?
  3. Audience appropriateness — is each post written at the right level?
  4. Completeness — are the key findings present in each post?

  Be strict. A score of 8 or above means approved=True. Below 8 means approved=False.

  Original Paper:
  Title: {paper.title}
  Findings: {paper.findings}
  Results: {paper.results}
  Conclusions: {paper.conclusions}
  Limitations: {paper.limitations}

  Technical Post Key Takeaways: {technical.key_takeaways}
  General Post Key Takeaways: {general.key_takeaways}
  ELI5 Post Key Takeaways: {eli5.key_takeaways}

  Technical Post Content:
  {technical.content[:1000]}

  General Post Content:
  {general.content[:1000]}

  ELI5 Post Content:
  {eli5.content[:1000]}
  """

    result = model.invoke([HumanMessage(content=prompt)])
    current_count = state.get("revision_count", 0)
    return {
        "verdict": result,
        "revision_count": current_count + 1
    }


# ── Routing Function ───────────────────────────────────────────────────────

def route_after_judge(state: PaperState) -> str:
    verdict = state["verdict"]
    revision_count = state.get("revision_count", 0)

    if verdict.approved:
        return "end"
    if revision_count >= 2:
        return "end"
    return "revise"


# ── Graph ──────────────────────────────────────────────────────────────────

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
        import json
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
