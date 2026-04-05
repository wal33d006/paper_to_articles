from langchain_core.messages import HumanMessage
from agents.models import JudgeVerdict, PaperState
from agents.model import get_model


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


def route_after_judge(state: PaperState) -> str:
    verdict = state["verdict"]
    revision_count = state.get("revision_count", 0)

    if verdict.approved:
        return "end"
    if revision_count >= 2:
        return "end"
    return "revise"
