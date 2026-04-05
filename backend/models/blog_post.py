from pydantic import BaseModel, Field


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
