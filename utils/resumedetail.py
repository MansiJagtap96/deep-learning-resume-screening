# =========================================
# 📁 utils/resumedetail.py
# =========================================

import fitz  # PyMuPDF
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
import google.generativeai as genai


# =========================================
# 0️⃣ GEMINI SETUP
# =========================================

GEMINI_API_KEY = "AIzaSyAIHNT9Vybjv5vycics60hovlfrEIbLaSw"   # 🔥 replace this
genai.configure(api_key=GEMINI_API_KEY)

gemini_model = genai.GenerativeModel("gemini-3-flash-preview")


# =========================================
# 1️⃣ LOAD EMBEDDING MODEL
# =========================================

print("🔄 Loading Resume Detail Models...")

EMBED_MODEL_PATH = "ats_resume_matcher"
embed_model = SentenceTransformer(EMBED_MODEL_PATH)

print("✅ Resume Detail Models Loaded")


# =========================================
# 2️⃣ PDF TEXT EXTRACTION
# =========================================

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# =========================================
# 3️⃣ SKILL MATCHING
# =========================================

def skill_match(resume_text, skills):
    matched = []
    for skill in skills:
        if skill.lower() in resume_text.lower():
            matched.append(skill)
    return matched


# =========================================
# 4️⃣ GEMINI HR EXPLANATION
# =========================================

def generate_hr_explanation(job_text, resume_text, match_percent,
                            matched_core, matched_secondary,
                            missing_core, missing_secondary):

    prompt = f"""
You are a professional HR ATS evaluation assistant.

Job Details:
{job_text}

Match Score: {match_percent}%

Matched Core Skills: {matched_core}
Matched Secondary Skills: {matched_secondary}

Missing Core Skills: {missing_core}
Missing Secondary Skills: {missing_secondary}

Resume Content:
{resume_text[:3000]}

Generate a clean HR evaluation report.

IMPORTANT RULES:
- Do NOT use markdown symbols like ####, **, *, or ---
- Do NOT use bullet symbols like *, -, etc.
- Write in plain clean text
- Use simple numbered headings like:

1. Overall Match Summary
2. Key Strengths
3. Skill Gaps
4. Experience Evaluation
5. Final Hiring Recommendation

Keep it professional, clean, and readable.
"""

    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating explanation: {str(e)}"

# =========================================
# 5️⃣ MAIN ANALYSIS FUNCTION
# =========================================

def analyze_resumee(resume_path, job_title, job_description, core_skills, secondary_skills):

    resume_text = extract_text_from_pdf(resume_path)

    job_text = (
        f"Job Title: {job_title}\n"
        f"Job Description: {job_description}\n"
        f"Core Skills: {', '.join(core_skills)}\n"
        f"Secondary Skills: {', '.join(secondary_skills)}"
    )

    # --- Embeddings
    job_embedding = embed_model.encode(job_text, normalize_embeddings=True)
    resume_embedding = embed_model.encode(resume_text, normalize_embeddings=True)

    similarity = float(np.dot(job_embedding, resume_embedding))
    semantic_score = similarity * 100

    # --- Skill Matching
    matched_core = skill_match(resume_text, core_skills)
    matched_secondary = skill_match(resume_text, secondary_skills)

    core_score = (len(matched_core) / len(core_skills)) * 30 if core_skills else 0
    secondary_score = (len(matched_secondary) / len(secondary_skills)) * 10 if secondary_skills else 0

    # --- Final Score
    final_score = round((semantic_score * 0.6) + core_score + secondary_score, 2)

    # --- Explanation via Gemini
    explanation = generate_hr_explanation(
        job_text,
        resume_text,
        final_score,
        matched_core,
        matched_secondary,
        list(set(core_skills) - set(matched_core)),
        list(set(secondary_skills) - set(matched_secondary))
    )

    return {
        "final_score": final_score,
        "explanation": explanation
    }