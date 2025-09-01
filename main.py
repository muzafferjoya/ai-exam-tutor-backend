# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import supabase
from ai_engine import (
    generate_study_plan,
    generate_notes_bilingual,
    generate_quiz
)
from pydantic import BaseModel
from datetime import datetime, timedelta
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-exam-tutor-frontend.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterUser(BaseModel):
    email: str
    exam_type: str
    study_hours: int

class GenerateNotesRequest(BaseModel):
    topic: str

class GenerateQuizRequest(BaseModel):
    topic: str

class SubmitQuizRequest(BaseModel):
    user_id: str
    answers: list

@app.post("/register")
async def register_user(data: RegisterUser):
    user_data = {
        "email": data.email,
        "exam_type": data.exam_type,
        "study_hours": data.study_hours
    }
    result = supabase.table("users").insert(user_data).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="User registration failed")
    
    user_id = result.data[0]["id"]

    supabase.table("progress").insert({
        "user_id": user_id,
        "streak": 0,
        "accuracy": 0.0,
        "last_active_date": str(datetime.today().date())
    }).execute()

    return {"message": "User registered", "user_id": user_id}

@app.get("/study-plan/{user_id}")
async def get_study_plan(user_id: str):
    user = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    user = user.data[0]
    plan = generate_study_plan(user["exam_type"], user["study_hours"])
    return {"study_plan": plan}

@app.post("/notes")
async def generate_notes(req: GenerateNotesRequest):
    notes = generate_notes_bilingual(req.topic)
    return notes

@app.post("/quiz")
async def create_quiz(req: GenerateQuizRequest):
    questions = generate_quiz(req.topic)
    return {"questions": questions}

@app.post("/quiz/submit")
async def submit_quiz(req: SubmitQuizRequest):
    # Mock quiz ID for now
    score = sum(1 for a in req.answers if a == 0)
    total = 10
    percentage = (score / total) * 100

    # Update progress
    progress = supabase.table("progress").select("*").eq("user_id", req.user_id).execute().data[0]
    new_streak = progress["streak"]
    today = datetime.today().date()

    if progress["last_active_date"] != str(today):
        if progress["last_active_date"] == str(today - timedelta(days=1)):
            new_streak += 1
        else:
            new_streak = 1
        supabase.table("progress").update({
            "streak": new_streak,
            "last_active_date": str(today)
        }).eq("user_id", req.user_id).execute()

    quizzes = supabase.table("quizzes").select("score").eq("user_id", req.user_id).execute().data
    scores = [q["score"] for q in quizzes if q["score"] is not None]
    avg_accuracy = (sum(scores) / (len(scores) * 10)) * 100 if scores else 0

    supabase.table("progress").update({"accuracy": avg_accuracy}).eq("user_id", req.user_id).execute()

    return {
        "score": score,
        "total": total,
        "percentage": round(percentage, 1),
        "correct_answers": [0]*10,
        "explanations": ["Sample explanation"]*10
    }

@app.get("/progress/{user_id}")
async def get_progress(user_id: str):
    progress = supabase.table("progress").select("*").eq("user_id", user_id).execute()
    if not progress.data:
        raise HTTPException(status_code=404, detail="Progress not found")
    data = progress.data[0]
    quizzes_attempted = supabase.table("quizzes").select("*", count='exact').eq("user_id", user_id).execute().count
    return {
        "streak": data["streak"],
        "accuracy": round(data["accuracy"], 1),
        "quizzes_attempted": quizzes_attempted
    }
