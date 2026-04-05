from langchain_core.messages import HumanMessage
from agents.models import PaperContent, PaperState
from agents.model import get_model


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
