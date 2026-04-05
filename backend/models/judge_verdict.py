from pydantic import BaseModel, Field


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
