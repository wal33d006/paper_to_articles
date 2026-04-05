from typing import TypedDict

from backend.models.paper_content import PaperContent
from backend.models.simplified_content import SimplifiedContent
from backend.models.blog_post import BlogPost
from backend.models.judge_verdict import JudgeVerdict


class PaperState(TypedDict):
    raw_text: str
    paper_content: PaperContent
    simplified: SimplifiedContent
    technical_post: BlogPost
    general_post: BlogPost
    eli5_post: BlogPost
    verdict: JudgeVerdict
    revision_count: int
