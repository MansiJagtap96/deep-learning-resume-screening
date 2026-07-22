import os
import json
import pdfplumber
from docx import Document
from google import genai

client = genai.Client()


# -------- TEXT EXTRACTION --------
def extract_text(file_path):
    if file_path.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text

    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError("Only PDF or DOCX supported")


# -------- PROMPT BUILDER --------
def build_prompt(resume_text):
    return f"""
You are an expert resume analyst, career coach, and ATS specialist.
Analyze the following resume text and provide a deep, professional evaluation.

Resume Text:
\"\"\"{resume_text}\"\"\"

Your task:
1. Create a concise professional summary of the candidate.
2. Identify the strongest skills, experiences, and achievements.
3. Detect gaps or weaknesses.
4. Evaluate ATS readiness.
5. Suggest improvements.
6. Recommend suitable roles.

Return output strictly in JSON format:

{{
  "professional_summary": "...",
  "key_strengths": ["...", "..."],
  "identified_gaps": ["...", "..."],
  "ats_feedback": "...",
  "improvement_suggestions": ["...", "..."],
  "recommended_roles": ["...", "..."]
}}
"""


# -------- GEMINI ANALYSIS --------
def analyze_resume(file_path):
    resume_text = extract_text(file_path)
    prompt = build_prompt(resume_text)

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    raw_text = response.text

    # Extract JSON safely
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    json_part = raw_text[start:end]

    try:
        parsed = json.loads(json_part)
    except:
        parsed = {"error": "Failed to parse Gemini response", "raw": raw_text}

    return parsed