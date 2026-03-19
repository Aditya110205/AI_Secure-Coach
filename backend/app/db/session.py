from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/ai_chat"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()