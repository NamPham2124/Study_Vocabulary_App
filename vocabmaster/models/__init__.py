"""Models root package."""

from vocabmaster.models.base import (
    Language,
    ScriptPreference,
    BaseVocabCreate,
    BaseVocabUpdate,
    BaseVocabResponse,
)
from vocabmaster.models.auth import (
    UserRegister,
    UserLogin,
    UserSettingsUpdate,
    TokenResponse,
    UserResponse,
)
from vocabmaster.models.paths import (
    LearningPathCreate,
    LearningPathUpdate,
    LearningPathResponse,
)
from vocabmaster.models.factory import validate_language_fields

__all__ = [
    "Language",
    "ScriptPreference",
    "BaseVocabCreate",
    "BaseVocabUpdate",
    "BaseVocabResponse",
    "UserRegister",
    "UserLogin",
    "UserSettingsUpdate",
    "TokenResponse",
    "UserResponse",
    "LearningPathCreate",
    "LearningPathUpdate",
    "LearningPathResponse",
    "validate_language_fields",
]
