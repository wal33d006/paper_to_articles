from pydantic import BaseModel, Field
from typing import TypedDict


class PaperContent(BaseModel):
    title: str = Field(
        description="Title of the paper"
    )
    authors: list[str] = Field(
        description="List of authors"
    )
    keywords: list[str] = Field(
        description="Keywords from the paper"
    )
    abstract: str = Field(
        description="Abstract from the paper"
    )
    methodology: str = Field(
        description="Methodology from the paper"
    )
    findings: str = Field(
        description="Findings from the paper"
    )
    results: str = Field(
        description="Results from the paper"
    )
    conclusions: str = Field(
        description="Conclusions from the paper"
    )
    limitations: str = Field(
        description="Limitations from the paper"
    )


class SimplifiedContent(BaseModel):
    core_insight: str = Field(
        description="The single most important discovery or conclusion of the paper, explained in one plain English "
                    "sentence that anyone can understand"
    )
    why_it_matters: str = Field(
        description="A practical explanation of why this research is significant and how it could impact the real "
                    "world or a specific field"
    )
    real_world_analogy: str = Field(
        description="A relatable everyday analogy that explains the core concept of the paper, starting with 'It is "
                    "like...'"
    )
    jargon_map: dict[str, str] = Field(
        description="A dictionary mapping technical terms and acronyms from the paper to their plain English "
                    "equivalents"
    )


class BlogPost(BaseModel):
    target_audience: str = Field(
        description="The intended audience for this blog post: 'technical', 'general', or 'eli5'"
    )
    title: str = Field(
        description="A compelling, audience-appropriate title for the blog post that accurately represents the "
                    "paper's findings"
    )
    content: str = Field(
        description="The full blog post in markdown format, written specifically for the target audience in "
                    "appropriate language and depth"
    )
    key_takeaways: list[str] = Field(
        description="3 to 5 concise bullet points summarizing the most important points from the blog post, used for "
                    "accuracy verification"
    )


class JudgeVerdict(BaseModel):
    approved: bool = Field(
        description="True if all three blog posts accurately represent the paper and are appropriate for their target "
                    "audiences, False if any need revision"
    )
    overall_score: int = Field(
        description="Overall quality score from 1 to 10 across all three posts, where 10 means publication-ready and "
                    "1 means major inaccuracies"
    )
    feedback_per_post: dict[str, str] = Field(
        description="Specific actionable feedback for each post keyed by audience type: 'technical', 'general', "
                    "'eli5'. Only populated if approved is False"
    )
    accuracy_concerns: list[str] = Field(
        description="A list of specific factual errors or misrepresentations found across any of the three posts "
                    "compared to the original paper"
    )


class PaperState(TypedDict):
    raw_text: str
    paper_content: PaperContent
    simplified: SimplifiedContent
    technical_post: BlogPost
    general_post: BlogPost
    eli5_post: BlogPost
    verdict: JudgeVerdict
    revision_count: int
