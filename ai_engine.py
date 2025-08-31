# backend/ai_engine.py
import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def groq_prompt(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 600
    }
    response = requests.post(GROQ_URL, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Groq error: {response.text}")
    return response.json()["choices"][0]["message"]["content"].strip()

def generate_study_plan(exam_type: str, hours_per_day: int) -> str:
    prompt = f"Generate a {hours_per_day}-hour daily study plan for {exam_type} exam. Example: '1.5 hrs Quant | 1 hr Reasoning | 30 mins GK'"
    return groq_prompt(prompt)

def generate_notes_bilingual(topic: str) -> dict:
    prompt = f"Generate notes on '{topic}' in English (bullet points), then in Hindi. Format: ### English\\n- ...\\n### Hindi\\n- ..."
    content = groq_prompt(prompt)
    parts = content.split("### Hindi")
    english = parts[0].replace("### English", "").strip()
    hindi = parts[1].strip() if len(parts) > 1 else "नोट्स उपलब्ध नहीं हैं।"
    return {"english": english, "hindi": hindi}

def generate_quiz(topic: str) -> list:
    prompt = f"Generate 10 MCQs on '{topic}' with A/B/C/D, Correct: letter, Explanation:. Format: Q1: ...\nA: ...\nCorrect: A\nExplanation: ..."
    raw = groq_prompt(prompt)
    return parse_quiz(raw)

def parse_quiz(raw: str) -> list:
    lines = raw.strip().split('\n')
    questions = []
    current = None
    for line in lines:
        line = line.strip()
        if line.startswith("Q") and ":" in line:
            if current: questions.append(current)
            current = {"question": line.split(":",1)[1].strip(), "options":[], "correct":0, "explanation":""}
        elif line.startswith(("A:", "B:", "C:", "D:")):
            current["options"].append(line[2:].strip())
        elif line.startswith("Correct:"):
            current["correct"] = ord(line[-1]) - ord('A')
        elif line.startswith("Explanation:"):
            current["explanation"] = line.split(":",1)[1].strip()
    if current: questions.append(current)
    return questions[:10]
