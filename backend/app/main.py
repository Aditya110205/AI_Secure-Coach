import hashlib
from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.user import User
from app.models.chat import Chat
from app.utils.security import generate_key

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Coach - Secure Chat")
app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "AI Coach Backend Running"}


@app.get("/create-user")
def create_user():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "aditya").first()
        if existing:
            return {"msg": "User already exists", "user_id": existing.id}

        password = "test123"
        key = generate_key(password)

        user = User(
            username="aditya",
            password_hash=hashlib.sha256(password.encode()).hexdigest(),
            encryption_key=key.decode()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"msg": "User created", "user_id": user.id}
    finally:
        db.close()