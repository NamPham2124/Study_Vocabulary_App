"""Pydantic schemas for authentication and user settings."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    interface_language: str = "vi"
    active_learning_language: str = "en"
    has_selected_language: bool = False
    script_preference: str = "hans"


class UserLogin(BaseModel):
    email: str = Field(..., min_length=1, max_length=128, description="Email address or username")
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    email: str
    interface_language: str = "vi"
    active_learning_language: str = "en"
    has_selected_language: bool = False
    english_voice_preference: str = "en-US"
    chinese_voice_preference: str = "zh-CN"
    script_preference: str = "hans"
    daily_new_target: int = 10
    daily_review_target: int = 50


class UserSettingsUpdate(BaseModel):
    interface_language: Optional[str] = None
    active_learning_language: Optional[str] = None
    has_selected_language: Optional[bool] = None
    english_voice_preference: Optional[str] = None
    chinese_voice_preference: Optional[str] = None
    script_preference: Optional[str] = None
    timezone: Optional[str] = None
    daily_new_target: Optional[int] = Field(None, ge=1, le=100)
    daily_review_target: Optional[int] = Field(None, ge=1, le=500)
    daily_time_goal: Optional[int] = Field(None, ge=5, le=180)


class WorkspaceSelectRequest(BaseModel):
    language: str = Field("en", pattern=r"^(en|zh)$")
    script_preference: Optional[str] = "hans"


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    interface_language: str = "vi"
    active_learning_language: str = "en"
    has_selected_language: bool = False
    english_voice_preference: str = "en-US"
    chinese_voice_preference: str = "zh-CN"
    script_preference: str = "hans"
    timezone: str = "Asia/Ho_Chi_Minh"
    daily_new_target: int = 10
    daily_review_target: int = 50
    daily_time_goal: int = 20
    created_at: str

