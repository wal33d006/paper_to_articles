from pydantic import BaseModel, Field


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
