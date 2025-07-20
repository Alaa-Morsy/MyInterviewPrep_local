
import os
from typing import Optional
from google import genai
from Questions import QuestionGenerateResponse

async def generate_interview_questions(job_title: str,num_technical:int, num_behavioral:int):
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        prompt=f"""You are an interview preparation system asked by the user to generate {num_behavioral} behavioral Questions and {num_technical} technical Questions for his upcoming interview for a {job_title} position.""",
        temperature=0.5,
        max_output_tokens=1024,
        config={
        "response_mime_type": "application/json",
        "response_schema": list[QuestionGenerateResponse],
        }
    )
    if response.status != 200:
        raise Exception(f"Error generating questions: {response.status} - {response.text}")
    return response.text
