import os
import numpy as np
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from flask import current_app

# Load model once (IMPORTANT)
MODEL_PATH = "ats_resume_matcher"
model = SentenceTransformer(MODEL_PATH)

def summarize_resume(application):
    """
    Very simple summary (can upgrade later with LLM)
    """

    resume_path = os.path.join(current_app.root_path, application.resume)

    if not os.path.exists(resume_path):
        return "Resume file not found."

    resume_text = extract_text_from_pdf(resume_path)

    # Basic summary: first 800 characters
    summary = resume_text[:800]

    return summary if summary else "No readable content found."

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def rank_applications(job, applications, top_n=None):
    """
    job → Job object
    applications → list of Application objects
    top_n → number admin entered
    """

    job_text = (
        f"Job Title: {job.title}\n"
        f"Job Description: {job.description}"
    )

    job_embedding = model.encode(job_text, normalize_embeddings=True)

    ranked_results = []

    for app in applications:
        # absolute resume path
        resume_path = os.path.join(current_app.root_path, app.resume)

        if not os.path.exists(resume_path):
            continue

        resume_text = extract_text_from_pdf(resume_path)
        resume_embedding = model.encode(resume_text, normalize_embeddings=True)

        similarity = float(np.dot(job_embedding, resume_embedding))
        match_percent = round(similarity * 100, 2)

        ranked_results.append({
            "application": app,
            "match_percent": match_percent
        })

    # Sort by similarity
    ranked_results.sort(key=lambda x: x["match_percent"], reverse=True)

    # Return only top N if provided
    if top_n:
        ranked_results = ranked_results[:top_n]

    return ranked_results
