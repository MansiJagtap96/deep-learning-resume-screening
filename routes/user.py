import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.job import Job
from utils.llamaresume import analyze_resume
from models.application import Application
from models.user import db

user_bp = Blueprint("user", __name__, url_prefix="/user")


# -------- USER DASHBOARD --------
@user_bp.route("/dashboard")
@login_required
def dashboard():
    jobs = Job.query.all()
    return render_template("user/dashboard.html", jobs=jobs)


# -------- APPLY JOB --------
@user_bp.route("/apply/<int:job_id>", methods=["GET", "POST"])
@login_required
def apply(job_id):
    job = Job.query.get_or_404(job_id)

    # Prevent duplicate apply
    existing_application = Application.query.filter_by(
        user_id=current_user.id,
        job_id=job.id
    ).first()

    if existing_application:
        flash("You have already applied for this job.")
        return redirect(url_for("user.dashboard"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        resume = request.files["resume"]

        if resume and resume.filename.endswith(".pdf"):
            filename = secure_filename(resume.filename)

            # Generate unique filename
            unique_filename = str(uuid.uuid4()) + "_" + filename

            # Absolute upload folder path
            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "resumes"
            )

            # Create folder if not exists
            os.makedirs(upload_folder, exist_ok=True)

            # Full file save path
            resume_path = os.path.join(upload_folder, unique_filename)

            # Save file
            resume.save(resume_path)

            # Store relative path in DB
            db_resume_path = f"static/resumes/{unique_filename}"

            application = Application(
                user_id=current_user.id,
                job_id=job.id,
                name=name,
                email=email,
                phone=phone,
                resume=db_resume_path,
                status="Pending"
            )

            db.session.add(application)
            db.session.commit()

            flash("Application submitted successfully!")
            return redirect(url_for("user.dashboard"))

        else:
            flash("Please upload a valid PDF resume.")
            return redirect(request.url)

    return render_template("user/apply.html", job=job)


# -------- COMPARE JOB --------
from utils.ats_matcher import rank_applications
from models.application import Application
@user_bp.route("/compare/<int:job_id>", methods=["GET", "POST"])
@login_required
def compare(job_id):
    job = Job.query.get_or_404(job_id)

    if request.method == "POST":
        resume = request.files["resume"]
        action = request.form.get("action")  # <-- detect button

        if resume and resume.filename.endswith(".pdf"):
            filename = secure_filename(resume.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename

            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "temp_resumes"
            )
            os.makedirs(upload_folder, exist_ok=True)

            resume_path = os.path.join(upload_folder, unique_filename)
            resume.save(resume_path)

            # ---------- IF MATCH BUTTON ----------
            if action == "match":

                temp_application = Application(
                    user_id=current_user.id,
                    job_id=job.id,
                    name=current_user.username,
                    email=current_user.email,
                    phone=current_user.phone,
                    resume=f"static/temp_resumes/{unique_filename}",
                    status="Temp"
                )

                ranked = rank_applications(job, [temp_application])
                match_percent = ranked[0]["match_percent"] if ranked else 0

                return render_template(
                    "user/compare.html",
                    job=job,
                    match_percent=match_percent
                )

            # ---------- IF SUMMARY BUTTON ----------
            elif action == "summary":

                try:
                    summary_data = analyze_resume(resume_path)
                except Exception as e:
                    summary_data = {
                        "professional_summary": "Error generating summary.",
                        "key_strengths": [],
                        "identified_gaps": [],
                        "ats_feedback": str(e),
                        "improvement_suggestions": [],
                        "recommended_roles": []
                    }

                return render_template(
                    "user/compare.html",
                    job=job,
                    summary=summary_data
                )

        flash("Please upload a valid PDF file.")
        return redirect(request.url)

    return render_template("user/compare.html", job=job)

# -------- MY APPLICATIONS --------
@user_bp.route("/my-applications")
@login_required
def my_applications():
    applications = Application.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "user/my_applications.html",
        applications=applications
    )



