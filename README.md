# AI Email Agent

An AI-powered email drafting tool built with FastAPI and Google Gemini.

## Features
- Generate polished email drafts from a simple description
- Choose tone: Professional, Friendly, Assertive, Formal, or Casual
- Refine drafts with natural language instructions
- One-click open in your mail app

## Stack
- **Backend:** FastAPI + Google Gemini API
- **Frontend:** Vanilla HTML/CSS/JS
- **Hosted on:** Hugging Face Spaces

## Setup
1. Clone the repo
2. Add your `GEMINI_API_KEY` as an environment variable
3. Run with `uvicorn app:app --host 0.0.0.0 --port 7860`
