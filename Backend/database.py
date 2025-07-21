from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker
import os 
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.types import Enum as SqlEnum
from Questions import QuestionType

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:     
        yield db
    finally: 
        db.close() 

class Question(Base):
    __tablename__ = "questions" 
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_title = Column(String, index=True)
    question_type = Column(SqlEnum(QuestionType, name="question_type_enum"), nullable=False)
    question = Column(String)       
    difficulty = Column(String, nullable=True)  # stores QuestionDifficulty enum as string
    flagged = Column(Boolean, default=False)    
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 

