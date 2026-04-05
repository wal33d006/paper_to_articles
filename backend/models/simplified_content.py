from pydantic import BaseModel, Field


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
