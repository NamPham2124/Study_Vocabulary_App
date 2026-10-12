"""Vietnamese language vocabulary models and validation."""

from typing import Optional
from pydantic import BaseModel, Field


class VietnameseFields(BaseModel):
    tone: Optional[str] = Field(
        None, pattern=r"^(ngang|huyền|sắc|hỏi|ngã|nặng)$"
    )
    sino_vietnamese: Optional[str] = Field(None, description="Hán-Việt root (e.g. 幸福 -> hạnh phúc)")
    northern_pronunciation: Optional[str] = None
    southern_pronunciation: Optional[str] = None
