import json
from sqlalchemy.orm import Session
from app.models.chat import Chat
from app.models.user import User
from app.utils.security import encrypt_data, decrypt_data
from app.services.gemini import get_mood_score


def save_chat(db: Session, user_id: int, message: str, ai_response: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    key = user.encryption_key.encode()

    mood = get_mood_score(message)

    chat_data = {
        "user": message,
        "ai": ai_response
    }

    encrypted_chat = encrypt_data(json.dumps(chat_data), key)

    new_chat = Chat(
        user_id=user_id,
        encrypted_chat=encrypted_chat,
        mood_score=mood
    )

    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat


def get_chats(db: Session, user_id: int, consent: bool):
    if not consent:
        return {"error": "User consent required"}

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    key = user.encryption_key.encode()
    chats = db.query(Chat).filter(Chat.user_id == user_id).all()

    decrypted = []
    for chat in chats:
        data = json.loads(decrypt_data(chat.encrypted_chat, key))
        data["mood_score"] = chat.mood_score
        data["timestamp"] = str(chat.created_at)
        decrypted.append(data)

    return decrypted


def get_recent_history(db: Session, user_id: int, limit: int = 5):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    key = user.encryption_key.encode()
    chats = db.query(Chat).filter(
        Chat.user_id == user_id
    ).order_by(Chat.created_at.desc()).limit(limit).all()

    history = []
    for chat in reversed(chats):
        try:
            data = json.loads(decrypt_data(chat.encrypted_chat, key))
            history.append(data)
        except:
            continue
    return history