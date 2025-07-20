from fastapi import FastAPI, HTTPException
from typing import List, Optional
from uuid import uuid4
import Questions as Q
from Gemini_Service import generate_interview_questions

app = FastAPI()

# --- In-memory storage for demo purposes ---
QUESTIONS_DB_GENERATED: List[Q.Question] = []
QUESTIONS_DB_User: List[Q.Question] = []


@app.post("/api/questions/generate")
async def generate_questions(req: Q.GenerateRequest,SaveToUserDB: Optional[bool] = False):
    # Validate the request
    if not req.job_title:
        raise HTTPException(status_code=400, detail="Job title is required")

    # Here integrating with Gemini Studio or another AI service
    Q.questions = await generate_interview_questions(
        job_title=req.job_title,
        num_technical= req.num_technical, 
        num_behavioral= req.num_behavioral  
    )
    # For now, return mock questions
    Q.questions = [
        Q.Question(
            id=str(uuid4()),
            job_title=req.job_title,
            question_type="technical",
            question=f"What are the benefits of asynchronous programming in Python?"
        ),
        Q.Question(
            id=str(uuid4()),
            job_title=req.job_title,
            question_type="behavioral",
            question=f"Describe a time you solved a conflict in a team."
        )
    ]

    if SaveToUserDB:
        # Save generated questions to user DB
        QUESTIONS_DB_GENERATED.extend(Q.questions)
        return {"questions": QUESTIONS_DB_GENERATED}
    else:
        # Return generated questions without saving
        return {"The following questions are not Saved ": Q.questions}

@app.get("/api/questions")
async def get_questions():
    if QUESTIONS_DB_GENERATED == []:
        raise HTTPException(status_code=404, detail="Please Generate or save questions first")
    return QUESTIONS_DB_GENERATED


@app.post("/api/questions")
async def modify_and_save_questions(question_id:str, difficulty:Optional[Q.QuestionDifficulty] = "medium", IsInterresting: Optional[bool] = False):
    # Modify pregenerated questions with difficulty and flagged, then save to user DB
    if not QUESTIONS_DB_GENERATED:
        raise HTTPException(status_code=400, detail="No questions to modify")
    id_found = False
    for q in QUESTIONS_DB_GENERATED :
        if q.id == question_id:
            q.difficulty = difficulty
            q.flagged = IsInterresting
            id_found = True
            break
    if not id_found:
        # If the question ID is not found, raise an error
        raise HTTPException(status_code=404, detail="Question not found")

    return {
        "message": "Questions saved and modified successfully",
        "questions": QUESTIONS_DB_GENERATED
    }

@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: str):
    for q in QUESTIONS_DB_GENERATED :
        if q.id == question_id:
            QUESTIONS_DB_GENERATED.remove(q)
        break
    return {"message": f"Question with id {question_id} deleted.",
            "Your questions": QUESTIONS_DB_GENERATED}

@app.get("/api/stats")
async def get_stats():
    return {"total_questions": 2, "most_common_topic": "Geography"}