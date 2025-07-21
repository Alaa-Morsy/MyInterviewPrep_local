from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

# Define Enums for QuestionType and QuestionDifficulty
class QuestionType(str, Enum):
    technical = "technical"
    behavioral = "behavioral"

class  QuestionDifficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

# Define the Question model
class Question(BaseModel):
    id: Optional[str]
    job_title: str
    question_type:QuestionType
    question: str
    difficulty: Optional[QuestionDifficulty] = None
    flagged: Optional[bool] = False


# Define the request model for generating questions
class GenerateRequest(BaseModel):
    job_title: str
    num_technical:Optional[int]=1
    num_behavioral:Optional[int]=1

# Define the response model for generating questions
class QuestionGenerateResponse(BaseModel):
    job_title: str
    question_type:QuestionType
    question: str
