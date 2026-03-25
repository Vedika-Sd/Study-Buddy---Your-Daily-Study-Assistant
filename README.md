# Study Buddy

Study Buddy is an AI-powered learning assistant that turns raw study material into summaries, practice questions, MCQs, answer feedback, and an interactive tutor chat.

It is built as a simple full-stack project with a `FastAPI` backend and a single-page `HTML/CSS/JavaScript` frontend, using NVIDIA-hosted `google/gemma-2-27b-it` through an OpenAI-compatible API.

## Problem Statement

Students often struggle to turn long notes or textbook content into something they can revise quickly and practice effectively. Reading alone is slow, passive, and does not always reveal whether the learner actually understands the topic.

## Solution

Study Buddy helps students study actively by taking learning material as input and instantly generating:

- concise summaries
- key points for revision
- conceptual and analytical questions
- MCQs with explanations
- answer evaluation with feedback
- contextual AI chat support

## Key Features

- `Smart Summary`: Converts long text into a short readable summary with key takeaways.
- `Question Generator`: Creates conceptual, analytical, and application-based study questions.
- `MCQ Creator`: Builds one-click multiple choice questions with answer explanations.
- `Answer Checker`: Scores student answers and suggests improvements.
- `Tutor Chat`: Lets students ask follow-up questions based on the same study material.
- `Reading Insights`: Shows word count and estimated reading time.

## Tech Stack

### Frontend

- `HTML5`
- `CSS3`
- `Vanilla JavaScript`
- `Google Fonts` for typography

### Backend

- `Python`
- `FastAPI`
- `Uvicorn`
- `Pydantic`
- `python-dotenv`

### AI / API Layer

- `OpenAI Python SDK` with NVIDIA's OpenAI-compatible endpoint
- `NVIDIA API`
- Model: `google/gemma-2-27b-it`

## How The Project Works

1. The user pastes study material into the frontend.
2. The frontend sends the text to the FastAPI backend.
3. The backend calls the NVIDIA-hosted Gemma model.
4. The AI returns structured JSON responses for each feature.
5. The frontend displays summaries, questions, MCQs, feedback, and chat replies in a clean interface.

## Project Structure

```text
Study Buddy/
|-- backend.py        # FastAPI backend and AI endpoints
|-- frontend.html     # Single-page frontend UI
|-- .env              # API key configuration
`-- README.md
```

## Frontend Overview

The frontend is a single-page interface designed to feel lightweight and easy to use.

- clean responsive layout
- modern typography and color system
- tab-based content sections
- API connection status check
- interactive answer checking and chat experience

## Backend Overview

The backend is built with FastAPI and exposes REST endpoints for all study features.

### Main Responsibilities

- receive study content from the frontend
- validate request data
- call the NVIDIA-hosted LLM
- parse structured JSON responses
- return clean API responses to the frontend

### API Endpoints

- `GET /`  
  Health check for backend status and model info.

- `POST /summarize`  
  Generates summary, key points, word count, and reading time.

- `POST /questions`  
  Generates 4 study questions.

- `POST /mcq`  
  Generates one MCQ with 4 options, correct answer, and explanation.

- `POST /check-answer`  
  Evaluates the student's answer and returns score, feedback, model answer, and improvements.

- `POST /chat`  
  Supports contextual multi-turn chat about the provided study material.

## Why These Technologies Were Used

- `FastAPI`: Fast, simple, and perfect for building clean AI APIs.
- `Pydantic`: Makes request and response validation easy.
- `Vanilla HTML/CSS/JS`: Keeps the project lightweight and beginner-friendly.
- `NVIDIA API + Gemma`: Provides AI capabilities for summarization, tutoring, and question generation.
- `python-dotenv`: Keeps API keys outside the code.

## Setup Instructions

### 1. Clone the project

```bash
git clone <your-repository-url>
cd "Study Buddy"
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn pydantic python-dotenv openai
```

### 4. Add environment variables

Create a `.env` file:

```env
NVIDIA_API_KEY=your_api_key_here
```

### 5. Run the backend

```bash
python backend.py
```

The API will run on:

```text
http://localhost:8000
```

### 6. Open the frontend

Open `frontend.html` in your browser.

The frontend is already configured to call:

```text
http://localhost:8000
```

## Sample Use Cases

- revise chapter notes quickly before an exam
- turn lecture content into practice questions
- test understanding with MCQs
- check written answers before submission
- ask doubts in a tutor-like chat flow

## Current Strengths

- simple architecture
- easy to run locally
- clear UI
- practical student-focused features
- structured AI responses

## Limitations

- no database or user authentication
- frontend is a single static file
- no saved chat or study history
- depends on external AI API availability
- no automated tests yet

## Future Improvements

- PDF or document upload support
- authentication and user profiles
- saved notes and revision history
- multiple quizzes per topic
- downloadable summaries
- deployment to cloud
- test coverage and better error handling

## Ideal Users

- students preparing for exams
- learners revising technical subjects
- anyone who wants quick AI-assisted study support

## Conclusion

Study Buddy is a clean and practical AI study assistant focused on helping students learn faster and more actively. It combines a lightweight frontend, a fast Python backend, and modern LLM capabilities to make studying more interactive, structured, and effective.
