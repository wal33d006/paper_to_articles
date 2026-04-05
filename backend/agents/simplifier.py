from langchain_core.messages import HumanMessage
from backend.models import SimplifiedContent, PaperState
from backend.model_helper import get_model


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
