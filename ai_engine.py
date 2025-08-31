# backend/ai_engine.py

import os
import requests

# Get Groq API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def groq_prompt(prompt: str) -> str:
    """
    Send prompt to Groq API and return response text
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",  # Fast, free, supports Hindi
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6,
        "max_tokens": 600,
        "stream": False
    }
    try:
        response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Groq API Error: {e}")
        raise Exception("Failed to generate content. Please try again.")

def generate_study_plan(exam_type: str, hours_per_day: int) -> str:
    prompt = f"""
You are an expert SSC/Railway exam coach.
Generate a realistic daily study plan for {hours_per_day} hours.
Exam: {exam_type}
Include subjects like Quantitative Aptitude, Reasoning, General Awareness, English/Hindi.
Return only the plan as a plain string.
Example: "1.5 hrs Quant | 1 hr Reasoning | 30 mins GK"
"""
    return groq_prompt(prompt)

def generate_notes_bilingual(topic: str) -> dict:
    prompt = f"""
Generate concise, exam-focused notes on '{topic}' for Indian competitive exams.
First in English (use bullet points), then in Hindi (same format).
Do not add extra commentary.

Structure:
### English
- Key point 1
- Key point 2

### Hindi
- मुख्य बिंदु 1
- मुख्य बिंदु 2
"""
    content = groq_prompt(prompt)
    try:
        parts = content.split("### Hindi")
        english = parts[0].replace("### English", "").strip()
        hindi = parts[1].strip() if len(parts) > 1 else "नोट्स उपलब्ध नहीं हैं।"
    except:
        english = "Notes could not be generated."
        hindi = "नोट्स उत्पन्न नहीं किए जा सके।"
    
    return {"english": english, "hindi": hindi}

def generate_quiz(topic: str) -> list:
    prompt = f"""
Generate 10 multiple-choice questions on '{topic}' for SSC/Railway exams.
Each question must have 4 options (A, B, C, D), one correct answer, and explanation.

Format:
Q1: What is the capital of India?
A: Mumbai
B: Kolkata
C: New Delhi
D: Chennai
Correct: C
Explanation: New Delhi is the capital of India.

Q2: ...
"""
    raw_text = groq_prompt(prompt)
    return parse_quiz(raw_text)

def parse_quiz(raw: str) -> list:
    """
    Parse raw Groq response into structured quiz
    """
    lines = raw.strip().split('\n')
    questions = []
    current = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("Q") and ":" in line:
            if current: questions.append(current)
            q_num, q_text = line.split(":", 1)
            current = {
                "question": q_text.strip(),
                "options": [],
                "correct": None,
                "explanation": ""
            }
        elif line.startswith(("A:", "B:", "C:", "D:")):
            current["options"].append(line[2:].strip())
        elif line.startswith("Correct:"):
            letter = line.split(":")[1].strip().upper()
            if len(letter) == 1 and letter in "ABCD":
                current["correct"] = ord(letter) - ord('A')
        elif line.startswith("Explanation:"):
            current["explanation"] = line.split(":", 1)[1].strip()

    if current: questions.append(current)
    return questions[:10]  # Ensure only 10
