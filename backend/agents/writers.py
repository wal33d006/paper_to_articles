from langchain_core.messages import HumanMessage
from backend.models import BlogPost, PaperState
from backend.model import get_model


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
