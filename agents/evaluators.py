import os
from deepeval import evaluate
from deepeval.metrics import FaithfulnessMetric, GEval, SummarizationMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.evaluate.configs import AsyncConfig, DisplayConfig, ErrorConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.config import config


# ── Custom Gemini model for DeepEval ───────────────────────────────────────

class GeminiForDeepEval(DeepEvalBaseLLM):
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=config.google_api_key,
            temperature=0
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        from langchain_core.messages import HumanMessage
        response = self.model.invoke([HumanMessage(content=prompt)])
        return response.content

    async def a_generate(self, prompt: str) -> str:
        from langchain_core.messages import HumanMessage
        response = await self.model.ainvoke([HumanMessage(content=prompt)])
        return response.content

    def get_model_name(self) -> str:
        return config.model_name


def get_deepeval_model():
    return GeminiForDeepEval()


# ── Build test cases from pipeline output ──────────────────────────────────

def build_test_cases(result: dict, raw_text: str) -> list[LLMTestCase]:
    paper = result.get("paper_content")
    technical = result.get("technical")
    general = result.get("general")
    eli5 = result.get("eli5")

    if not paper or not technical:
        print(f"Missing data — paper: {bool(paper)}, technical: {bool(technical)}")
        return []

    source_context = [
        f"Title: {paper.get('title', '')}",
        f"Findings: {paper.get('findings', '')}",
        f"Results: {paper.get('results', '')}",
        f"Conclusions: {paper.get('conclusions', '')}",
        f"Limitations: {paper.get('limitations', '')}",
    ]

    def get_content(post):
        if isinstance(post, dict):
            return post.get("content", "")
        return getattr(post, "content", "") if post else ""

    def get_title(post):
        if isinstance(post, dict):
            return post.get("title", "")
        return getattr(post, "title", "") if post else ""

    technical_case = LLMTestCase(
        input=f"Write a technical blog post about: {get_title(technical)}",
        actual_output=get_content(technical),
        retrieval_context=source_context,
        additional_metadata={"audience": "technical"}
    )

    general_case = LLMTestCase(
        input=f"Write a general audience blog post about: {get_title(general)}",
        actual_output=get_content(general),
        retrieval_context=source_context,
        additional_metadata={"audience": "general"}
    )

    eli5_case = LLMTestCase(
        input=f"Write a beginner-friendly blog post about: {get_title(eli5)}",
        actual_output=get_content(eli5),
        retrieval_context=source_context,
        additional_metadata={"audience": "eli5"}
    )

    return [technical_case, general_case, eli5_case]


# ── Define metrics ─────────────────────────────────────────────────────────

# def get_faithfulness_metric():
#     return FaithfulnessMetric(
#         threshold=0.7,
#         model=get_deepeval_model(),
#         include_reason=True
#     )


def get_audience_metric():
    return GEval(
        name="AudienceAlignment",
        criteria="""
  Evaluate whether the blog post is written at the appropriate level for its
  target audience based on vocabulary complexity, depth of explanation,
  use of jargon, and assumed prior knowledge.

  A technical post should use precise terminology and go deep on methodology.
  A general post should be accessible to educated non-specialists without jargon.
  An ELI5 post should use simple words, analogies, and be understandable to a child.
  """,
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT
        ],
        threshold=0.7,
        model=get_deepeval_model()
    )


# def get_coverage_metric():
#     return SummarizationMetric(
#         threshold=0.5,
#         model=get_deepeval_model(),
#         include_reason=True
#     )


# ── Run evaluations ────────────────────────────────────────────────────────

def run_evaluations(result: dict, raw_text: str) -> dict:
    os.environ["CONFIDENT_API_KEY"] = config.deepeval_api_key

    test_cases = build_test_cases(result, raw_text)

    if not test_cases:
        print("No test cases built — skipping evaluation.")
        return {}

    audience = get_audience_metric()

    eval_result = evaluate(
        test_cases=test_cases,
        metrics=[audience],
        async_config=AsyncConfig(run_async=True, max_concurrent=3),
        display_config=DisplayConfig(show_indicator=False, print_results=True),
        error_config=ErrorConfig(ignore_errors=True),
    )

    audience_types = ["technical", "general", "eli5"]
    scores = {}

    for i, test_result in enumerate(eval_result.test_results):
        audience_type = audience_types[i] if i < len(audience_types) else f"case_{i}"
        case_scores = {}
        for metric_data in test_result.metrics_data:
            key = metric_data.name.lower().replace(" ", "_")
            case_scores[key] = {
                "score": metric_data.score,
                "reason": metric_data.reason,
                "passed": metric_data.success,
            }
        scores[audience_type] = case_scores

    return scores
