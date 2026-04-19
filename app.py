from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
import os
import urllib.parse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))

class DraftRequest(BaseModel):
    sender: str
    recipient: str
    purpose: str
    tone: str
    key_points: str
    extra_context: str

class RefineRequest(BaseModel):
    subject: str
    body: str
    recipient: str
    instruction: str

def call_gemini(prompt: str):
    try:
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        return response.text
    except Exception as e:
        e_str = str(e)
        if "429" in e_str or "quota" in e_str.lower():
            raise ValueError("Google Gemini ✦ : Looks like we've hit our limit. Give it a minute and try again.")
        elif "api key" in e_str.lower() or "invalid" in e_str.lower():
            raise ValueError("Google Gemini ✦ : Hmm, something's off with the setup. We're on it.")
        else:
            raise ValueError("Google Gemini ✦ : Oops! That didn't go as planned. Try again in a bit.")

def parse_email(raw: str):
    lines = raw.strip().split("\n")
    subject, body_lines = "", []
    for i, line in enumerate(lines):
        if line.lower().startswith("subject:"):
            subject = line[8:].strip()
            body_lines = lines[i+1:]
            break
    else:
        body_lines = lines
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    return subject, "\n".join(body_lines)

def build_mailto(recipient, subject, body):
    return f"mailto:{recipient}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"

@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("index.html")

@app.post("/draft")
async def draft(req: DraftRequest):
    if not req.sender or "@" not in req.sender:
        return {"error": "⚠️ Invalid sender email."}
    if not req.recipient or "@" not in req.recipient:
        return {"error": "⚠️ Invalid recipient email."}
    if not req.purpose.strip():
        return {"error": "⚠️ Please describe the purpose of the email."}

    prompt = f"""You are an expert email writer. Draft a professional email.

From: {req.sender}
To: {req.recipient}
Purpose: {req.purpose}
Tone: {req.tone}
Key Points: {req.key_points or 'None'}
Extra Context: {req.extra_context or 'None'}

Output format:
Line 1: Subject: <subject>
Line 2: blank
Line 3+: Full email body with greeting, paragraphs, closing, name.
No commentary outside the email."""

    try:
        result = call_gemini(prompt)
    except ValueError as e:
        return {"error": str(e)}

    subject, body = parse_email(result)
    return {"subject": subject, "body": body, "mailto": build_mailto(req.recipient, subject, body)}

@app.post("/refine")
async def refine(req: RefineRequest):
    if not req.body.strip():
        return {"error": "⚠️ No draft to refine."}
    if not req.instruction.strip():
        return {"error": "⚠️ Please enter a refinement instruction."}

    prompt = f"""You are an expert email editor.

Current email:
Subject: {req.subject}
---
{req.body}
---

Instruction: "{req.instruction}"

Rewrite applying the instruction. Output format:
Line 1: Subject: <subject>
Line 2: blank
Line 3+: Full revised body.
No commentary."""

    try:
        result = call_gemini(prompt)
    except ValueError as e:
        return {"error": str(e)}

    subject, body = parse_email(result)
    return {"subject": subject, "body": body, "mailto": build_mailto(req.recipient, subject, body)}