from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session , Mapped
from fastapi.middleware.cors import CORSMiddleware 
from typing import List, Optional
import json
from uuid import uuid4
import Questions as Q
import database as mydb
from database import Base, engine
from Gemini_Service import generate_interview_questions
from uuid import UUID

Base.metadata.create_all(bind=engine)
app = FastAPI()

# Set up CORS
app.add_middleware(
        CORSMiddleware, 
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"], ) 
# --- In-memory storage for demo purposes ---
QUESTIONS_DB_GENERATED: List[Q.Question] = []
QUESTIONS_DB_User: List[Q.Question] = []


@app.post("/api/questions/generate")
async def generate_questions(req: Q.GenerateRequest):
    # Validate the request
    if not req.job_title:
        raise HTTPException(status_code=400, detail="Job title is required")

    # Here integrating with Gemini Studio or another AI service
    try:
        response = await generate_interview_questions(
            job_title=req.job_title.lower(),
            num_technical=req.num_technical,
            num_behavioral=req.num_behavioral
        )
        if response is None:
            raise HTTPException(status_code=500, detail=f"No Generated Questions : PLease try again")

        Q.questions = []
        for item in response:
            question_obj = Q.Question(
            id=str(uuid4()),
            question=item.question,
            question_type=item.question_type,
            job_title=item.job_title,
            )
            Q.questions.append(question_obj)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")
    QUESTIONS_DB_GENERATED.extend(Q.questions)
    return {"questions": Q.questions}

@app.get("/api/questions",response_model=List[Q.Question])
async def get_questions( 
    question_id: Optional[str] = None,
    job_title: Optional[str] = None,
    question_type: Optional[Q.QuestionType] = None,
    question_difficulty: Optional[Q.QuestionDifficulty] = None,
    is_flagged: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(mydb.get_db) ):


    query = db.query(mydb.Question)
    if query.count() == 0:
        raise HTTPException(status_code=404, detail="No questions found in the database")
    try:
        if question_id:
            try:
                uuid_obj = UUID(question_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid UUID format for question_id")
            query = query.filter(mydb.Question.id == question_id)

        if job_title:
            query = query.filter(mydb.Question.job_title == job_title.lower())
        if question_type:   
            query = query.filter(mydb.Question.question_type == question_type)
        if question_difficulty:
            query = query.filter(mydb.Question.difficulty == question_difficulty)
        if is_flagged is not None:
            query = query.filter(mydb.Question.flagged == is_flagged)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid filter parameters: {str(e)}")
    
    questions = query.offset(skip).limit(limit).all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found with the specified filters")
    # Convert SQLAlchemy models to Q.Question Pydantic models
    result = [
        Q.Question(
            id=str(q.id),
            question=q.question,
            question_type=q.question_type,
            job_title=q.job_title,
            difficulty=q.difficulty,
            flagged=q.flagged
        )
        for q in questions
    ]
    return result


@app.post("/api/questions")
async def create_question(
    question_id: str,
    difficulty: Optional[Q.QuestionDifficulty] = "medium",
    is_interesting: Optional[bool] = False, 
    db: Session = Depends(mydb.get_db)):
        # Validate that question_id is a valid UUID
    try:
        uuid_obj = UUID(question_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format for question_id")
    
# Modify pregenerated questions with difficulty and flagged, then save to user DB
    if not QUESTIONS_DB_GENERATED:
        raise HTTPException(status_code=400, detail="No questions to modify")
    id_found = False
    for q in QUESTIONS_DB_GENERATED :
        if q.id == question_id:
            # Create a new Question object to save to the database
            db_question = mydb.Question(
             question=q.question,
             question_type=q.question_type,
             job_title=q.job_title,
             difficulty= difficulty,
             flagged=is_interesting) 
            
            db.add(db_question)
            db.commit()
            db.refresh(db_question) 
            id_found = True
            break
    if not id_found:
        # If the question ID is not found, raise an error
        raise HTTPException(status_code=404, detail="Question not found")

    return db_question 


@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: str, db: Session = Depends(mydb.get_db)): 
    # Validate that question_id is a valid UUID
    try:
        uuid_obj = UUID(question_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format for question_id")
    
    question = db.query(mydb.Question).filter(mydb.Question.id == question_id).first()
    if not question: 
        raise HTTPException(status_code=404, detail="Question not found")
        
    db.delete(question)
    db.commit()
    return {"detail": "Question deleted successfully"} 

@app.get("/api/stats")
async def get_stats(db: Session = Depends(mydb.get_db)):
    # Total questions
    total_questions = db.query(mydb.Question).count()

    # Count by difficulty
    difficulties = ["easy", "medium", "hard"]
    questions_by_difficulty = {
        diff: db.query(mydb.Question).filter(mydb.Question.difficulty == diff).count()
        for diff in difficulties
    }

    # Job titles and their counts
    job_titles = db.query(mydb.Question.job_title).distinct().all()
    job_titles = [jt[0] for jt in job_titles]
    questions_by_job = {
        job: db.query(mydb.Question).filter(mydb.Question.job_title == job).count()
        for job in job_titles
    }

    # Flagged questions count
    flagged_questions = db.query(mydb.Question).filter(mydb.Question.flagged == True).count()

    return {
        "total_questions": total_questions,
        "questions_by_difficulty": questions_by_difficulty,
        "questions_by_job": questions_by_job,
        "flagged_questions": flagged_questions
    }