"""
Study Buddy - FastAPI Backend
Powered by NVIDIA API (google/gemma-2-27b-it) via OpenAI-compatible client
NOTE: Gemma does not support system role — instructions are merged into user message
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import re

import dotenv
dotenv.load_dotenv()

from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

MODEL = "google/gemma-2-27b-it"

app = FastAPI(title="Study Buddy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response Models ────────────────────────────────────────────────

class TextInput(BaseModel):
    text: str

class SummaryResponse(BaseModel):
    summary: str
    key_points: list[str]
    word_count: int
    reading_time_minutes: float

class Question(BaseModel):
    id: int
    question: str
    type: str
    hint: str

class QuestionsResponse(BaseModel):
    questions: list[Question]

class MCQOption(BaseModel):
    label: str
    text: str

class MCQResponse(BaseModel):
    question: str
    options: list[MCQOption]
    correct_answer: str
    explanation: str
    difficulty: str

class AnswerCheckInput(BaseModel):
    text: str
    question: str
    user_answer: str

class AnswerCheckResponse(BaseModel):
    score: int
    feedback: str
    model_answer: str
    improvements: list[str]

class ChatInput(BaseModel):
    text: str
    conversation: list[dict]
    message: str

class ChatResponse(BaseModel):
    reply: str

# ── Helper ───────────────────────────────────────────────────────────────────

def ask_nvidia(instruction: str, user_content: str) -> str:
    """
    Single-turn call to NVIDIA Gemma model.
    Gemma does NOT support 'system' role — so we combine instruction + user
    content into a single user message.
    """
    combined_message = f"{instruction}\n\n{user_content}"

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": combined_message}
        ],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=True
    )

    full_response = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content

    return full_response


def ask_nvidia_chat(context: str, messages: list[dict]) -> str:
    """
    Multi-turn chat. Gemma has no system role, so we prepend the context
    instruction into the very first user message of the conversation.
    messages = [{"role": "user"|"assistant", "content": "..."}]
    """
    if not messages:
        raise ValueError("No messages provided")

    # Inject context into first user message
    formatted = []
    for i, m in enumerate(messages):
        role = "user" if m["role"] == "user" else "assistant"
        if i == 0 and role == "user":
            # Prepend context to the first user message
            content = f"{context}\n\nStudent question: {m['content']}"
        else:
            content = m["content"]
        formatted.append({"role": role, "content": content})

    completion = client.chat.completions.create(
        model=MODEL,
        messages=formatted,
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=True
    )

    full_response = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content

    return full_response

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Study Buddy API is running!", "version": "1.0.0", "model": MODEL}


@app.post("/summarize", response_model=SummaryResponse)
async def summarize(input: TextInput):
    text = input.text.strip()
    if len(text) < 50:
        raise HTTPException(status_code=400, detail="Text too short (min 50 chars).")

    instruction = """You are an expert academic summarizer.
Return ONLY valid JSON — no markdown fences, no explanation, no extra text.
Use exactly this structure:
{
  "summary": "2-4 paragraph concise summary as a single string",
  "key_points": ["point 1", "point 2", "point 3", "point 4", "point 5"]
}"""

    user = f"Summarize this study material:\n\n{text}"

    try:
        raw = ask_nvidia(instruction, user)
        raw = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI parsing error: {e} | Raw: {raw[:300]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

    word_count = len(text.split())
    reading_time = round(word_count / 200, 1)

    return SummaryResponse(
        summary=data["summary"],
        key_points=data.get("key_points", []),
        word_count=word_count,
        reading_time_minutes=reading_time,
    )


@app.post("/questions", response_model=QuestionsResponse)
async def generate_questions(input: TextInput):
    text = input.text.strip()
    if len(text) < 50:
        raise HTTPException(status_code=400, detail="Text too short.")

    instruction = """You are an expert educator creating study questions.
Return ONLY valid JSON — no markdown fences, no explanation, no extra text.
Use exactly this structure:
{
  "questions": [
    {"id": 1, "question": "...", "type": "conceptual", "hint": "Think about..."},
    {"id": 2, "question": "...", "type": "conceptual", "hint": "Consider..."},
    {"id": 3, "question": "...", "type": "analytical",  "hint": "Analyze..."},
    {"id": 4, "question": "...", "type": "application", "hint": "Apply..."}
  ]
}
Generate exactly 4 questions: 2 conceptual, 1 analytical, 1 application."""

    user = f"Generate study questions for this material:\n\n{text}"

    try:
        raw = ask_nvidia(instruction, user)
        raw = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI parsing error: {e} | Raw: {raw[:300]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

    return QuestionsResponse(questions=data["questions"])


@app.post("/mcq", response_model=MCQResponse)
async def generate_mcq(input: TextInput):
    text = input.text.strip()
    if len(text) < 50:
        raise HTTPException(status_code=400, detail="Text too short.")

    instruction = """You are an expert exam question writer.
Return ONLY valid JSON — no markdown fences, no explanation, no extra text.
Use exactly this structure:
{
  "question": "...",
  "options": [
    {"label": "A", "text": "..."},
    {"label": "B", "text": "..."},
    {"label": "C", "text": "..."},
    {"label": "D", "text": "..."}
  ],
  "correct_answer": "A",
  "explanation": "Why this answer is correct...",
  "difficulty": "medium"
}
One clearly correct answer, three plausible distractors. difficulty must be easy, medium, or hard."""

    user = f"Create a multiple-choice question from this material:\n\n{text}"

    try:
        raw = ask_nvidia(instruction, user)
        raw = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI parsing error: {e} | Raw: {raw[:300]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

    return MCQResponse(**data)


@app.post("/check-answer", response_model=AnswerCheckResponse)
async def check_answer(input: AnswerCheckInput):
    instruction = """You are a helpful tutor grading a student's answer.
Return ONLY valid JSON — no markdown fences, no explanation, no extra text.
Use exactly this structure:
{
  "score": 85,
  "feedback": "Overall assessment of the answer...",
  "model_answer": "The ideal complete answer...",
  "improvements": ["specific suggestion 1", "specific suggestion 2"]
}
Score 0-100 based on accuracy, depth, and clarity."""

    user = f"""Study Material:
{input.text}

Question: {input.question}

Student's Answer: {input.user_answer}

Grade this answer and return JSON only."""

    try:
        raw = ask_nvidia(instruction, user)
        raw = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI parsing error: {e} | Raw: {raw[:300]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

    return AnswerCheckResponse(**data)


@app.post("/chat", response_model=ChatResponse)
async def chat(input: ChatInput):
    """Context-aware multi-turn chat about the study material."""
    context = f"""You are Study Buddy, a friendly and knowledgeable AI tutor.
The student is studying this material:
---
{input.text[:2000]}
---
Answer clearly, use examples, encourage the student. Keep replies under 200 words."""

    messages = input.conversation[-10:]
    messages.append({"role": "user", "content": input.message})

    try:
        reply = ask_nvidia_chat(context, messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

    return ChatResponse(reply=reply)


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)