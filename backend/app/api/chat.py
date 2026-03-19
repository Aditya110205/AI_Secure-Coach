from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.services.gemini import get_ai_response
from app.services.chat_service import save_chat, get_chats, get_recent_history

router = APIRouter()


@router.post("/chat")
def chat(user_id: int, message: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User {user_id} not found. Call GET /create-user first."
        )

    history = get_recent_history(db, user_id, limit=5)
    ai_response = get_ai_response(message, history)
    save_chat(db, user_id, message, ai_response)

    return {
        "user": message,
        "ai": ai_response
    }


@router.get("/chats")
def read_chats(user_id: int, consent: bool, db: Session = Depends(get_db)):
    return get_chats(db, user_id, consent)


@router.get("/mood-trend")
def mood_trend(user_id: int, consent: bool, db: Session = Depends(get_db)):
    if not consent:
        raise HTTPException(status_code=403, detail="User consent required")

    from app.models.chat import Chat
    chats = db.query(Chat).filter(
        Chat.user_id == user_id
    ).order_by(Chat.created_at.asc()).limit(30).all()

    return {
        "mood_trend": [
            {"timestamp": str(c.created_at), "mood_score": c.mood_score}
            for c in chats
        ]
    }