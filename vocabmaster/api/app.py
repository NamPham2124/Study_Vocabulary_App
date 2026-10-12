"""FastAPI Application providing REST endpoints for VocabMaster."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Header,
    Query,
    UploadFile,
    File,
    Request,
    status,
)
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from vocabmaster.api.ui import HTML_CONTENT
from vocabmaster.auth.security import hash_password, verify_password
from vocabmaster.auth.tokens import (
    create_access_token,
    decode_access_token,
    AuthenticationError,
)
from vocabmaster.auth.access_control import enforce_ownership, AccessDeniedError
from vocabmaster.db.connection import get_db, DatabaseManager
from vocabmaster.db.migrations import init_db
from vocabmaster.db import repository
from vocabmaster.models.auth import (
    UserRegister,
    UserLogin,
    UserSettingsUpdate,
    WorkspaceSelectRequest,
    TokenResponse,
    UserResponse,
)
from vocabmaster.models.paths import (
    LearningPathCreate,
    LearningPathUpdate,
    LearningPathResponse,
)
from vocabmaster.models.base import (
    Language,
    BaseVocabCreate,
    BaseVocabUpdate,
)
from vocabmaster.models.factory import validate_language_fields
from vocabmaster.importer.processor import (
    import_vocabulary_file,
    preview_vocabulary_import,
    parse_tabular_text,
    DedupMode,
)
from vocabmaster.session import manager as session_manager


class DeckCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    target_language: Language = Language.EN
    tags: Optional[List[str]] = None
    max_new_cards_per_day: Optional[int] = Field(None, ge=1, le=500)
    max_reviews_per_day: Optional[int] = Field(None, ge=1, le=1000)
    daily_goal: Optional[str] = None
    preferred_duration: Optional[int] = Field(None, ge=5, le=120)
    status: Optional[str] = "active"
    icon: Optional[str] = None
    color: Optional[str] = None


class DeckUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_language: Optional[Language] = None
    tags: Optional[List[str]] = None
    max_new_cards_per_day: Optional[int] = Field(None, ge=1, le=500)
    max_reviews_per_day: Optional[int] = Field(None, ge=1, le=1000)
    daily_goal: Optional[str] = None
    preferred_duration: Optional[int] = Field(None, ge=5, le=120)
    status: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class StartSessionRequest(BaseModel):
    deck_id: Optional[str] = None
    path_id: Optional[str] = None
    session_type: Optional[str] = None
    learning_language: Optional[str] = None
    new_card_limit: Optional[int] = None
    review_limit: Optional[int] = None
    unlimited: bool = False


class SubmitAnswerRequest(BaseModel):
    rating: int = Field(..., ge=0, le=5)
    exercise_type: str = "flashcard"
    user_response: str = ""
    time_spent_seconds: float = 0.0
    requeue_failed_cards: bool = True


class PasteImportRequest(BaseModel):
    text_data: str = Field(..., min_length=1)
    filename: str = "pasted_table.tsv"
    dedup_strategy: DedupMode = "skip"


class RelationshipCreateRequest(BaseModel):
    target_vocab_id: str
    relation_type: str = "root_word"
    notes: str = ""


class PracticeSubmitRequest(BaseModel):
    vocab_id: Optional[str] = None
    practice_type: str = "sentence_writing"
    prompt: str
    user_text: str
    model_answer: str = ""
    self_assessment_score: int = Field(4, ge=1, le=5)


def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """Dependency to extract and authenticate current user from Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = authorization[7:].strip()
    try:
        payload = decode_access_token(token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    db_path = getattr(request.app.state, "db_path", None)
    with get_db(db_path) as conn:
        user = repository.get_user_by_id(conn, user_id)
        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or account deactivated",
            )
        return user


def create_app(db_path: Optional[str] = None) -> FastAPI:
    """Application factory for VocabMaster."""
    init_db(db_path)

    app = FastAPI(
        title="VocabMaster API",
        version="1.0.0",
        description="Spaced Repetition & Multilingual Vocabulary Management Engine",
    )
    app.state.db_path = db_path

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    @app.get("/api/health")
    def health():
        return {"status": "ok", "app": "VocabMaster", "version": "1.0.0"}

    @app.get("/", response_class=HTMLResponse)
    @app.get("/app", response_class=HTMLResponse)
    def index():
        return HTML_CONTENT

    # -----------------------------------------------------------------------
    # Authentication & User Settings
    # -----------------------------------------------------------------------

    @app.post("/api/auth/register", response_model=TokenResponse)
    def register(req: UserRegister):
        with get_db(db_path) as conn:
            if repository.get_user_by_email(conn, req.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
            if repository.get_user_by_username(conn, req.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )

            user_id = str(uuid.uuid4())
            pwd_hash, salt = hash_password(req.password)
            user = repository.create_user(
                conn,
                user_id=user_id,
                username=req.username,
                email=req.email,
                password_hash=pwd_hash,
                salt=salt,
                interface_language=req.interface_language,
                active_learning_language=req.active_learning_language,
                script_preference=req.script_preference,
            )

            token = create_access_token({"sub": user["id"], "username": user["username"]})
            return TokenResponse(
                access_token=token,
                user_id=user["id"],
                username=user["username"],
                email=user["email"],
                interface_language=user.get("interface_language", "vi"),
                active_learning_language=user.get("active_learning_language", "en"),
                has_selected_language=bool(user.get("has_selected_language", False)),
                english_voice_preference=user.get("english_voice_preference", "en-US"),
                chinese_voice_preference=user.get("chinese_voice_preference", "zh-CN"),
                script_preference=user.get("script_preference", "hans"),
                daily_new_target=user.get("daily_new_target", 10),
                daily_review_target=user.get("daily_review_target", 50),
            )

    @app.post("/api/auth/login", response_model=TokenResponse)
    def login(req: UserLogin):
        with get_db(db_path) as conn:
            ident = req.email.strip()
            user = repository.get_user_by_email(conn, ident.lower())
            if not user:
                user = repository.get_user_by_username(conn, ident)
            if not user or not verify_password(req.password, user["password_hash"], user["salt"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            token = create_access_token({"sub": user["id"], "username": user["username"]})
            return TokenResponse(
                access_token=token,
                user_id=user["id"],
                username=user["username"],
                email=user["email"],
                interface_language=user.get("interface_language", "vi"),
                active_learning_language=user.get("active_learning_language", "en"),
                has_selected_language=bool(user.get("has_selected_language", False)),
                english_voice_preference=user.get("english_voice_preference", "en-US"),
                chinese_voice_preference=user.get("chinese_voice_preference", "zh-CN"),
                script_preference=user.get("script_preference", "hans"),
                daily_new_target=user.get("daily_new_target", 10),
                daily_review_target=user.get("daily_review_target", 50),
            )

    @app.post("/api/users/workspace")
    def select_workspace(
        req: WorkspaceSelectRequest, user: Dict[str, Any] = Depends(get_current_user)
    ):
        with get_db(db_path) as conn:
            updated = repository.update_user_settings(
                conn,
                user["id"],
                active_learning_language=req.language,
                script_preference=req.script_preference or "hans",
                has_selected_language=1,
            )
            return {
                "status": "ok",
                "active_learning_language": updated.get("active_learning_language", req.language),
                "has_selected_language": bool(updated.get("has_selected_language", 1)),
                "script_preference": updated.get("script_preference", "hans"),
            }

    @app.get("/api/auth/me", response_model=UserResponse)
    def me(user: Dict[str, Any] = Depends(get_current_user)):
        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            is_active=bool(user["is_active"]),
            interface_language=user.get("interface_language", "vi"),
            active_learning_language=user.get("active_learning_language", "en"),
            has_selected_language=bool(user.get("has_selected_language", False)),
            english_voice_preference=user.get("english_voice_preference", "en-US"),
            chinese_voice_preference=user.get("chinese_voice_preference", "zh-CN"),
            script_preference=user.get("script_preference", "hans"),
            timezone=user.get("timezone", "Asia/Ho_Chi_Minh"),
            daily_new_target=user.get("daily_new_target", 10),
            daily_review_target=user.get("daily_review_target", 50),
            daily_time_goal=user.get("daily_time_goal", 20),
            created_at=user["created_at"],
        )

    @app.put("/api/auth/settings", response_model=UserResponse)
    def update_settings(req: UserSettingsUpdate, user: Dict[str, Any] = Depends(get_current_user)):
        with get_db(db_path) as conn:
            updated = repository.update_user_settings(
                conn, user["id"], **req.model_dump(exclude_unset=True)
            )
            return UserResponse(
                id=updated["id"],
                username=updated["username"],
                email=updated["email"],
                is_active=bool(updated["is_active"]),
                interface_language=updated.get("interface_language", "vi"),
                active_learning_language=updated.get("active_learning_language", "en"),
                has_selected_language=bool(updated.get("has_selected_language", False)),
                english_voice_preference=updated.get("english_voice_preference", "en-US"),
                chinese_voice_preference=updated.get("chinese_voice_preference", "zh-CN"),
                script_preference=updated.get("script_preference", "hans"),
                timezone=updated.get("timezone", "Asia/Ho_Chi_Minh"),
                daily_new_target=updated.get("daily_new_target", 10),
                daily_review_target=updated.get("daily_review_target", 50),
                daily_time_goal=updated.get("daily_time_goal", 20),
                created_at=updated["created_at"],
            )

    # -----------------------------------------------------------------------
    # Learning Paths Endpoints
    # -----------------------------------------------------------------------

    @app.post("/api/paths", response_model=LearningPathResponse)
    def create_path(req: LearningPathCreate, user: Dict[str, Any] = Depends(get_current_user)):
        path_id = str(uuid.uuid4())
        with get_db(db_path) as conn:
            try:
                path = repository.create_learning_path(
                    conn,
                    path_id=path_id,
                    user_id=user["id"],
                    name=req.name,
                    description=req.description,
                    learning_language=req.learning_language.value,
                    objective=req.objective,
                    daily_new_target=req.daily_new_target,
                    daily_time_goal=req.daily_time_goal,
                    deck_ids=req.deck_ids,
                )
                return path
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/paths", response_model=List[LearningPathResponse])
    def list_paths(
        language: Optional[str] = Query(None),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            return repository.list_learning_paths_for_user(conn, user["id"], learning_language=language)

    @app.get("/api/paths/{path_id}", response_model=LearningPathResponse)
    def get_path(path_id: str, user: Dict[str, Any] = Depends(get_current_user)):
        with get_db(db_path) as conn:
            path = repository.get_learning_path_by_id(conn, path_id, user["id"])
            if not path:
                raise HTTPException(status_code=404, detail="Learning path not found")
            return path

    @app.put("/api/paths/{path_id}", response_model=LearningPathResponse)
    def update_path(
        path_id: str, req: LearningPathUpdate, user: Dict[str, Any] = Depends(get_current_user)
    ):
        with get_db(db_path) as conn:
            try:
                updated = repository.update_learning_path(
                    conn, path_id, user["id"], **req.model_dump(exclude_unset=True)
                )
                if not updated:
                    raise HTTPException(status_code=404, detail="Learning path not found")
                return updated
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

    @app.delete("/api/paths/{path_id}")
    def delete_path(path_id: str, user: Dict[str, Any] = Depends(get_current_user)):
        with get_db(db_path) as conn:
            success = repository.delete_learning_path(conn, path_id, user["id"])
            if not success:
                raise HTTPException(status_code=404, detail="Learning path not found")
            return {"deleted": True, "path_id": path_id}

    # -----------------------------------------------------------------------
    # Decks Endpoints (Vocabulary Sets)
    # -----------------------------------------------------------------------

    @app.post("/api/decks")
    def create_deck(req: DeckCreateRequest, user: Dict[str, Any] = Depends(get_current_user)):
        deck_id = str(uuid.uuid4())
        with get_db(db_path) as conn:
            deck = repository.create_deck(
                conn,
                deck_id=deck_id,
                user_id=user["id"],
                name=req.name,
                description=req.description,
                target_language=req.target_language.value,
                tags=req.tags,
                max_new_cards_per_day=req.max_new_cards_per_day,
                max_reviews_per_day=req.max_reviews_per_day,
                daily_goal=req.daily_goal,
                preferred_duration=req.preferred_duration,
                status=req.status or "active",
                icon=req.icon,
                color=req.color,
            )
            return deck

    @app.get("/api/decks")
    def list_decks(
        language: Optional[str] = Query(None),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            return repository.list_decks_for_user(conn, user["id"], learning_language=language)

    @app.get("/api/tags")
    def list_tags(
        language: Optional[str] = Query(None),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            return repository.list_user_tags(conn, user["id"], language=language)

    @app.post("/api/decks/seed-template")
    def seed_template_deck_endpoint(
        language: Optional[str] = Query(None),
        deck_name: Optional[str] = Query(None),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            lang = language or user.get("active_learning_language", "en")
            deck = repository.seed_sample_template_deck(conn, user_id=user["id"], language=lang, deck_name=deck_name)
            return deck

    @app.post("/api/decks/reset-all")
    def reset_all_vocabulary_endpoint(
        language: Optional[str] = Query(None),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            lang = language or user.get("active_learning_language", "en")
            deck = repository.reset_user_vocabulary(conn, user_id=user["id"], language=lang)
            return {"status": "ok", "message": "Đã xóa toàn bộ từ vựng và tạo bộ thẻ mẫu mới", "deck": deck}

    @app.get("/api/decks/{deck_id}")
    def get_deck(deck_id: str, user: Dict[str, Any] = Depends(get_current_user)):
        with get_db(db_path) as conn:
            deck = repository.get_deck_by_id(conn, deck_id, user["id"])
            if not deck:
                raise HTTPException(status_code=404, detail="Deck not found")
            return deck

    @app.put("/api/decks/{deck_id}")
    def update_deck(
        deck_id: str,
        req: DeckUpdateRequest,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            updates = req.model_dump(exclude_unset=True)
            if "target_language" in updates and updates["target_language"]:
                updates["target_language"] = updates["target_language"].value if hasattr(updates["target_language"], "value") else str(updates["target_language"])
            deck = repository.update_deck(
                conn,
                deck_id=deck_id,
                user_id=user["id"],
                **updates,
            )
            if not deck:
                raise HTTPException(status_code=404, detail="Deck not found")
            return deck

    @app.delete("/api/decks/{deck_id}")
    def delete_deck(
        deck_id: str,
        delete_vocabulary: bool = Query(False),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            success = repository.delete_deck(
                conn, deck_id, user["id"], delete_vocabulary=delete_vocabulary
            )
            if not success:
                raise HTTPException(status_code=404, detail="Deck not found")
            return {"deleted": True, "deck_id": deck_id, "vocabulary_deleted": delete_vocabulary}

    # -----------------------------------------------------------------------
    # Vocabulary Items Endpoints
    # -----------------------------------------------------------------------

    @app.post("/api/decks/{deck_id}/vocab")
    def create_vocabulary_item(
        deck_id: str,
        req: BaseVocabCreate,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            deck = repository.get_deck_by_id(conn, deck_id, user["id"])
            if not deck:
                raise HTTPException(status_code=404, detail="Deck not found")

            # Validate language specific fields
            validated_lang_fields = validate_language_fields(
                req.language, req.language_specific_fields
            )

            vocab_id = str(uuid.uuid4())
            item = repository.create_vocab_item(
                conn,
                {
                    "id": vocab_id,
                    "deck_id": deck_id,
                    "user_id": user["id"],
                    "language": req.language.value,
                    "term": req.term,
                    "definition": req.definition,
                    "ipa": req.ipa,
                    "part_of_speech": req.part_of_speech,
                    "examples": req.examples,
                    "synonyms": req.synonyms,
                    "antonyms": req.antonyms,
                    "notes": req.notes,
                    "tags": req.tags,
                    "root_word": req.root_word,
                    "root_word_id": req.root_word_id,
                    "vietnamese_meanings": req.vietnamese_meanings,
                    "english_definitions": req.english_definitions,
                    "mnemonics": req.mnemonics,
                    "audio_url": req.audio_url,
                    "is_favorite": req.is_favorite,
                    "language_specific_fields": validated_lang_fields,
                },
            )

            # Auto-create SRS card in NEW state
            card_id = str(uuid.uuid4())
            repository.create_srs_card(
                conn,
                {
                    "id": card_id,
                    "vocab_id": vocab_id,
                    "deck_id": deck_id,
                    "user_id": user["id"],
                    "state": "NEW",
                },
            )
            return item

    @app.post("/api/vocab")
    def create_vocabulary_standalone(
        req: BaseVocabCreate,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            deck = repository.get_deck_by_id(conn, req.deck_id, user["id"])
            if not deck:
                raise HTTPException(status_code=404, detail="Deck not found")

            # Validate language specific fields
            validated_lang_fields = validate_language_fields(
                req.language, req.language_specific_fields
            )

            vocab_id = str(uuid.uuid4())
            item = repository.create_vocab_item(
                conn,
                {
                    "id": vocab_id,
                    "deck_id": req.deck_id,
                    "user_id": user["id"],
                    "language": req.language.value,
                    "term": req.term.strip(),
                    "definition": req.definition.strip(),
                    "ipa": req.ipa.strip(),
                    "part_of_speech": req.part_of_speech.strip(),
                    "examples": req.examples,
                    "synonyms": req.synonyms,
                    "antonyms": req.antonyms,
                    "notes": req.notes.strip(),
                    "tags": req.tags,
                    "root_word": req.root_word.strip(),
                    "root_word_id": req.root_word_id,
                    "vietnamese_meanings": req.vietnamese_meanings or [req.definition.strip()],
                    "english_definitions": req.english_definitions,
                    "mnemonics": req.mnemonics.strip(),
                    "audio_url": req.audio_url,
                    "is_favorite": req.is_favorite,
                    "language_specific_fields": validated_lang_fields,
                },
            )

            # Auto-link root word if text match exists in deck
            if req.root_word and not req.root_word_id:
                root_match = repository.find_vocab_by_term(conn, req.deck_id, req.root_word.strip())
                if root_match:
                    repository.update_vocab_item(conn, vocab_id, user["id"], {"root_word_id": root_match["id"]})
                    repository.create_word_relationship(
                        conn,
                        rel_id=str(uuid.uuid4()),
                        user_id=user["id"],
                        source_vocab_id=vocab_id,
                        target_vocab_id=root_match["id"],
                        relation_type="root_word",
                        notes="Linked root word",
                    )

            # Auto-create SRS card in NEW state
            card_id = str(uuid.uuid4())
            repository.create_srs_card(
                conn,
                {
                    "id": card_id,
                    "vocab_id": vocab_id,
                    "deck_id": req.deck_id,
                    "user_id": user["id"],
                    "state": "NEW",
                },
            )
            return item

    @app.get("/api/decks/{deck_id}/vocab")
    def list_vocabulary(
        deck_id: str,
        search: Optional[str] = Query(None),
        part_of_speech: Optional[str] = Query(None),
        is_favorite: Optional[bool] = Query(None),
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            deck = repository.get_deck_by_id(conn, deck_id, user["id"])
            if not deck:
                raise HTTPException(status_code=404, detail="Deck not found")

            items = repository.list_vocab_items(
                conn,
                deck_id=deck_id,
                user_id=user["id"],
                search=search,
                part_of_speech=part_of_speech,
                is_favorite=is_favorite,
                limit=limit,
                offset=offset,
            )
            return items

    @app.get("/api/vocab")
    def list_all_vocabulary(
        language: Optional[str] = Query(None),
        path_id: Optional[str] = Query(None),
        part_of_speech: Optional[str] = Query(None),
        is_favorite: Optional[bool] = Query(None),
        search: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            items = repository.list_vocab_items(
                conn,
                user_id=user["id"],
                language=language,
                path_id=path_id,
                part_of_speech=part_of_speech,
                is_favorite=is_favorite,
                search=search,
                limit=limit,
                offset=offset,
            )
            return items

    @app.get("/api/vocab/{vocab_id}")
    def get_vocabulary(
        vocab_id: str, user: Dict[str, Any] = Depends(get_current_user)
    ):
        with get_db(db_path) as conn:
            item = repository.get_vocab_item_by_id(conn, vocab_id, user["id"])
            if not item:
                raise HTTPException(status_code=404, detail="Vocabulary item not found")
            return item

    @app.put("/api/vocab/{vocab_id}")
    def update_vocabulary(
        vocab_id: str,
        req: BaseVocabUpdate,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            item = repository.get_vocab_item_by_id(conn, vocab_id, user["id"])
            if not item:
                raise HTTPException(status_code=404, detail="Vocabulary item not found")

            updates = req.model_dump(exclude_unset=True)
            if "language_specific_fields" in updates and updates["language_specific_fields"]:
                target_lang = Language(updates.get("language") or item["language"])
                updates["language_specific_fields"] = validate_language_fields(
                    target_lang, updates["language_specific_fields"]
                )

            updated = repository.update_vocab_item(conn, vocab_id, user["id"], updates)
            return updated

    @app.post("/api/vocab/{vocab_id}/favorite")
    def toggle_favorite(
        vocab_id: str, user: Dict[str, Any] = Depends(get_current_user)
    ):
        with get_db(db_path) as conn:
            item = repository.get_vocab_item_by_id(conn, vocab_id, user["id"])
            if not item:
                raise HTTPException(status_code=404, detail="Vocabulary item not found")
            new_fav = not item.get("is_favorite", False)
            updated = repository.update_vocab_item(conn, vocab_id, user["id"], {"is_favorite": new_fav})
            return {"id": vocab_id, "is_favorite": new_fav}

    @app.delete("/api/vocab/{vocab_id}")
    def delete_vocabulary(
        vocab_id: str, user: Dict[str, Any] = Depends(get_current_user)
    ):
        with get_db(db_path) as conn:
            success = repository.delete_vocab_item(conn, vocab_id, user["id"])
            if not success:
                raise HTTPException(status_code=404, detail="Vocabulary item not found")
            return {"deleted": True, "vocab_id": vocab_id}

    # -----------------------------------------------------------------------
    # Word Relationships Endpoints (Root words, synonyms, etc.)
    # -----------------------------------------------------------------------

    @app.post("/api/vocab/{vocab_id}/relationships")
    def add_relationship(
        vocab_id: str,
        req: RelationshipCreateRequest,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            item = repository.get_vocab_item_by_id(conn, vocab_id, user["id"])
            target = repository.get_vocab_item_by_id(conn, req.target_vocab_id, user["id"])
            if not item or not target:
                raise HTTPException(status_code=404, detail="Source or target vocabulary not found")

            rel_id = str(uuid.uuid4())
            rel = repository.create_word_relationship(
                conn,
                rel_id=rel_id,
                user_id=user["id"],
                source_vocab_id=vocab_id,
                target_vocab_id=req.target_vocab_id,
                relation_type=req.relation_type,
                notes=req.notes,
            )
            return rel

    @app.get("/api/vocab/{vocab_id}/relationships")
    def get_relationships(
        vocab_id: str, user: Dict[str, Any] = Depends(get_current_user)
    ):
        with get_db(db_path) as conn:
            return repository.list_relationships_for_vocab(conn, vocab_id, user["id"])

    # -----------------------------------------------------------------------
    # File & Pasted Import Wizard Endpoints
    # -----------------------------------------------------------------------

    @app.post("/api/decks/{deck_id}/import/preview")
    async def preview_import(
        deck_id: str,
        file: Optional[UploadFile] = File(None),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        content = await file.read()
        with get_db(db_path) as conn:
            try:
                return preview_vocabulary_import(
                    conn=conn,
                    user_id=user["id"],
                    deck_id=deck_id,
                    file_bytes=content,
                    filename=file.filename or "preview.csv",
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/decks/{deck_id}/import")
    async def import_file(
        deck_id: str,
        file: UploadFile = File(...),
        dedup_strategy: DedupMode = Query("skip"),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        content = await file.read()
        with get_db(db_path) as conn:
            try:
                res = import_vocabulary_file(
                    conn=conn,
                    user_id=user["id"],
                    deck_id=deck_id,
                    file_bytes=content,
                    filename=file.filename or "import.csv",
                    dedup_strategy=dedup_strategy,
                )
                return {
                    "batch_id": res.batch_id,
                    "filename": res.filename,
                    "total_rows": res.total_rows,
                    "imported_count": res.imported_count,
                    "skipped_count": res.skipped_count,
                    "error_count": res.error_count,
                    "errors": res.errors,
                }
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/decks/{deck_id}/import/paste")
    def import_pasted_data(
        deck_id: str,
        req: PasteImportRequest,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        content = req.text_data.encode("utf-8")
        with get_db(db_path) as conn:
            try:
                res = import_vocabulary_file(
                    conn=conn,
                    user_id=user["id"],
                    deck_id=deck_id,
                    file_bytes=content,
                    filename=req.filename,
                    dedup_strategy=req.dedup_strategy,
                )
                return {
                    "batch_id": res.batch_id,
                    "filename": res.filename,
                    "total_rows": res.total_rows,
                    "imported_count": res.imported_count,
                    "skipped_count": res.skipped_count,
                    "error_count": res.error_count,
                    "errors": res.errors,
                }
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

    # -----------------------------------------------------------------------
    # Recoverable Daily Learning Sessions & SRS Endpoints
    # -----------------------------------------------------------------------

    @app.post("/api/sessions/start")
    def start_session(
        req: StartSessionRequest,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            if req.deck_id:
                deck = repository.get_deck_by_id(conn, req.deck_id, user["id"])
                if not deck:
                    raise HTTPException(status_code=404, detail="Deck not found")
            if req.path_id:
                path = repository.get_learning_path_by_id(conn, req.path_id, user["id"])
                if not path:
                    raise HTTPException(status_code=404, detail="Learning path not found")

            session_info = session_manager.start_or_resume_session(
                conn,
                user_id=user["id"],
                deck_id=req.deck_id,
                path_id=req.path_id,
                learning_language=req.learning_language,
                session_type=req.session_type,
                new_card_limit=req.new_card_limit,
                review_limit=req.review_limit,
                unlimited=req.unlimited,
            )
            return session_info

    @app.get("/api/sessions/active")
    def get_active_session(
        deck_id: Optional[str] = Query(None),
        path_id: Optional[str] = Query(None),
        learning_language: Optional[str] = Query(None),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            lang = learning_language or user.get("active_learning_language", "en")
            session = repository.get_active_or_paused_session(
                conn, user["id"], deck_id=deck_id, path_id=path_id, learning_language=lang
            )
            if not session:
                return {"active": False, "session": None, "current_card": None}
            current_card = session_manager.get_current_card(conn, session["id"], user["id"])
            return {"active": True, "session": session, "current_card": current_card}

    @app.post("/api/sessions/{session_id}/answer")
    def answer_card(
        session_id: str,
        req: SubmitAnswerRequest,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            try:
                res = session_manager.submit_card_answer(
                    conn=conn,
                    session_id=session_id,
                    user_id=user["id"],
                    rating=req.rating,
                    exercise_type=req.exercise_type,
                    user_response=req.user_response,
                    time_spent_seconds=req.time_spent_seconds,
                    requeue_failed_cards=req.requeue_failed_cards,
                )
                return res
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/sessions/{session_id}/advance-phase")
    def advance_session_phase(
        session_id: str,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            try:
                return session_manager.advance_phase(conn, session_id, user["id"])
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/sessions/{session_id}/pause")
    def pause_session(
        session_id: str,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            updated = session_manager.pause_session(conn, session_id, user["id"])
            if not updated:
                raise HTTPException(status_code=404, detail="Session not found")
            return updated

    @app.post("/api/sessions/{session_id}/resume")
    def resume_session(
        session_id: str,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            updated = session_manager.resume_session(conn, session_id, user["id"])
            if not updated:
                raise HTTPException(status_code=404, detail="Session not found")
            current_card = session_manager.get_current_card(conn, session_id, user["id"])
            return {"session": updated, "current_card": current_card}

    @app.post("/api/sessions/{session_id}/abandon")
    def abandon_session(
        session_id: str,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            updated = session_manager.abandon_session(conn, session_id, user["id"])
            if not updated:
                raise HTTPException(status_code=404, detail="Session not found")
            return updated

    @app.get("/api/sessions/{session_id}/summary")
    def get_summary(
        session_id: str,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            try:
                return session_manager.get_session_summary(conn, session_id, user["id"])
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

    @app.get("/api/reviews/due")
    def get_due_reviews_endpoint(
        deck_id: Optional[str] = Query(None),
        path_id: Optional[str] = Query(None),
        language: Optional[str] = Query(None),
        limit: int = Query(50, ge=1, le=500),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            lang = language or user.get("active_learning_language", "en")
            return repository.get_due_review_cards(
                conn,
                user_id=user["id"],
                deck_id=deck_id,
                path_id=path_id,
                learning_language=lang,
                limit=limit,
            )

    # -----------------------------------------------------------------------
    # Practice Submissions (Speaking & Writing)
    # -----------------------------------------------------------------------

    @app.post("/api/practice/submit")
    def submit_practice(
        req: PracticeSubmitRequest,
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        sub_id = str(uuid.uuid4())
        with get_db(db_path) as conn:
            sub = repository.create_practice_submission(
                conn,
                sub_id=sub_id,
                user_id=user["id"],
                vocab_id=req.vocab_id,
                practice_type=req.practice_type,
                prompt=req.prompt,
                user_text=req.user_text,
                model_answer=req.model_answer,
                self_assessment_score=req.self_assessment_score,
            )
            return sub

    @app.get("/api/practice")
    @app.get("/api/practice/history")
    def list_practice(
        limit: int = Query(20, ge=1, le=100),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            return repository.list_practice_submissions(conn, user["id"], limit=limit)

    # -----------------------------------------------------------------------
    # Progress, Calendar Heatmap, & Statistics
    # -----------------------------------------------------------------------

    @app.get("/api/stats")
    def stats(
        language: Optional[str] = Query(None),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            lang = language or user.get("active_learning_language", "en")
            counts = repository.get_due_and_new_counts(conn, user["id"], learning_language=lang)
            decks = repository.list_decks_for_user(conn, user["id"], learning_language=lang)
            streak = repository.get_user_streak(conn, user["id"], learning_language=lang)
            return {
                "active_learning_language": lang,
                "total_decks": len(decks),
                "total_cards": counts["total_cards"],
                "learned_cards": counts["learned_count"],
                "due_reviews_today": counts["due_count"],
                "new_cards_ready": counts["new_count"],
                "current_streak": streak["current_streak"],
                "longest_streak": streak["longest_streak"],
            }

    @app.get("/api/progress/streak")
    def streak_info(
        language: Optional[str] = Query(None),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            lang = language or user.get("active_learning_language", "en")
            return repository.get_user_streak(conn, user["id"], learning_language=lang)

    @app.get("/api/progress/calendar")
    def calendar(
        days: int = Query(90, ge=7, le=365),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            return repository.get_user_study_calendar(conn, user["id"], days=days)

    @app.get("/api/progress/skills")
    def skills(
        language: Optional[str] = Query(None),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            lang = language or user.get("active_learning_language", "en")
            return repository.get_skill_breakdown(conn, user["id"], learning_language=lang)

    return app


app = create_app()
