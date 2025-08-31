# AI Exam Tutor – Backend

🚀 FastAPI server for AI-powered exam prep (SSC + Railway)

## Features
- User registration
- AI Notes (Hindi + English) via Groq Llama 3
- AI Quiz generation (10 MCQs)
- Progress tracking
- Study plan generator

## Tech Stack
- Python 3.11
- FastAPI
- Groq API (Llama 3) – Free AI
- Supabase (PostgreSQL + Auth)
- Docker

## Setup

```bash
# Clone repo
git clone https://github.com/yourname/ai-exam-tutor-backend.git
cd ai-exam-tutor-backend

# Install dependencies
pip install -r requirements.txt

# Copy env
cp .env.example .env
# Add your keys in .env

# Run server
uvicorn main:app --reload
