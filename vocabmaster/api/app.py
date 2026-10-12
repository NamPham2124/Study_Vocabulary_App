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
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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
    TokenResponse,
    UserResponse,
)
from vocabmaster.models.base import (
    Language,
    BaseVocabCreate,
    BaseVocabUpdate,
)
from vocabmaster.models.factory import validate_language_fields
from vocabmaster.importer.processor import import_vocabulary_file, DedupMode
from vocabmaster.session import manager as session_manager


class DeckCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    target_language: Language = Language.EN


class DeckUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_language: Optional[Language] = None


class StartSessionRequest(BaseModel):
    deck_id: Optional[str] = None
    new_card_limit: Optional[int] = None
    review_limit: Optional[int] = None


class SubmitAnswerRequest(BaseModel):
    rating: int = Field(..., ge=0, le=5)
    time_spent_seconds: float = 0.0
    requeue_failed_cards: bool = True


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
    def health():
        return {"status": "ok", "app": "VocabMaster", "version": "1.0.0"}

    # -----------------------------------------------------------------------
    # Authentication Endpoints
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
            )

            token = create_access_token({"sub": user["id"], "username": user["username"]})
            return TokenResponse(
                access_token=token,
                user_id=user["id"],
                username=user["username"],
                email=user["email"],
            )

    @app.post("/api/auth/login", response_model=TokenResponse)
    def login(req: UserLogin):
        with get_db(db_path) as conn:
            user = repository.get_user_by_email(conn, req.email)
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
            )

    @app.get("/api/auth/me", response_model=UserResponse)
    def me(user: Dict[str, Any] = Depends(get_current_user)):
        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            is_active=bool(user["is_active"]),
            created_at=user["created_at"],
        )

    # -----------------------------------------------------------------------
    # Decks Endpoints
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
            )
            return deck

    @app.get("/api/decks")
    def list_decks(user: Dict[str, Any] = Depends(get_current_user)):
        with get_db(db_path) as conn:
            return repository.list_decks_for_user(conn, user["id"])

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
            deck = repository.update_deck(
                conn,
                deck_id=deck_id,
                user_id=user["id"],
                name=req.name,
                description=req.description,
                target_language=req.target_language.value if req.target_language else None,
            )
            if not deck:
                raise HTTPException(status_code=404, detail="Deck not found")
            return deck

    @app.delete("/api/decks/{deck_id}")
    def delete_deck(deck_id: str, user: Dict[str, Any] = Depends(get_current_user)):
        with get_db(db_path) as conn:
            success = repository.delete_deck(conn, deck_id, user["id"])
            if not success:
                raise HTTPException(status_code=404, detail="Deck not found")
            return {"deleted": True, "deck_id": deck_id}

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

    @app.get("/api/decks/{deck_id}/vocab")
    def list_vocabulary(
        deck_id: str,
        search: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            deck = repository.get_deck_by_id(conn, deck_id, user["id"])
            if not deck:
                raise HTTPException(status_code=404, detail="Deck not found")

            items = repository.list_vocab_items(
                conn, deck_id=deck_id, user_id=user["id"], search=search, limit=limit, offset=offset
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
    # File Import Endpoints (CSV & XLSX)
    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------
    # Recoverable Daily Learning Sessions Endpoints
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

            session_info = session_manager.start_or_resume_session(
                conn,
                user_id=user["id"],
                deck_id=req.deck_id,
                new_card_limit=req.new_card_limit,
                review_limit=req.review_limit,
            )
            return session_info

    @app.get("/api/sessions/active")
    def get_active_session(
        deck_id: Optional[str] = Query(None),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            session = repository.get_active_or_paused_session(conn, user["id"], deck_id)
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
                    time_spent_seconds=req.time_spent_seconds,
                    requeue_failed_cards=req.requeue_failed_cards,
                )
                return res
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

    @app.get("/api/sessions")
    def list_sessions(
        limit: int = Query(20, ge=1, le=100),
        user: Dict[str, Any] = Depends(get_current_user),
    ):
        with get_db(db_path) as conn:
            return repository.list_user_sessions(conn, user["id"], limit=limit)

    # -----------------------------------------------------------------------
    # Statistics & Overview
    # -----------------------------------------------------------------------

    @app.get("/api/stats")
    def stats(user: Dict[str, Any] = Depends(get_current_user)):
        with get_db(db_path) as conn:
            counts = repository.get_due_and_new_counts(conn, user["id"])
            decks = repository.list_decks_for_user(conn, user["id"])
            total_cards = sum(d.get("total_cards", 0) for d in decks)
            return {
                "total_decks": len(decks),
                "total_cards": total_cards,
                "due_reviews_today": counts["due_count"],
                "new_cards_ready": counts["new_count"],
            }

    return app
