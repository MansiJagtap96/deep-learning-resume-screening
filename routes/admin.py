from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.job import Job
from models.user import db
from models.application import Application
from utils.ats_matcher import rank_applications
from utils.llamaresume import analyze_resume
import os
from utils.resumedetail import analyze_resumee
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from types import SimpleNamespace

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# HARD-CODED ADMIN CREDENTIALS
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# EMAIL CONFIGURATION
EMAIL_USER = "jagtapmansi9296@gmail.com"
EMAIL_PASS = "yttf crph bamz ucms"


import random

def mask_name(name):
    if len(name) <= 2:
        return name

    masked = name[0] + "_%" + name[len(name)//2] + "_$" + name[-2:]
    return masked


def mask_email(email):
    try:
        username, domain = email.split("@")

        masked_user = username[0] + "_%" + username[-1]

        domain_name, domain_ext = domain.split(".")
        masked_domain = domain_name[0] + "_$" + domain_name[-1]

        return masked_user + "@" + masked_domain + "." + domain_ext
    except:
        return "hidden@email.com"



def send_selection_email(to_email, name, job_title):

    subject = "Job Application Status - Selected"

    body = f"""
Hello {name},

Congratulations!

You have been selected for the position: {job_title}.

Our recruitment team will contact you shortly for the next steps.

Best Regards,
Recruitment Team
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()

        print("Email sent successfully")

    except Exception as e:
        print("Email failed:", e)

def send_rejection_email(to_email, name, job_title):

    subject = "Job Application Status"

    body = f"""
Hello {name},

Thank you for applying for the position: {job_title}.

Unfortunately, you were not selected this time.

We wish you success in your future career.

Best Regards,
Recruitment Team
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()

    except Exception as e:
        print("Email failed:", e)


# --------- ADMIN AUTH CHECK ----------
def admin_login_required():
    if not session.get("admin_logged_in"):
        return False
    return True


# --------- ADMIN LOGIN ----------
@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin.dashboard"))

        flash("Invalid admin credentials")

    return render_template("admin/admin_login.html")


# --------- ADMIN DASHBOARD ----------
@admin_bp.route("/dashboard")
def dashboard():
    if not admin_login_required():
        return redirect(url_for("admin.admin_login"))

    jobs = Job.query.all()
    return render_template("admin/admin_dashboard.html", jobs=jobs)


# --------- ADD JOB ----------
@admin_bp.route("/add-job", methods=["GET", "POST"])
def add_job():
    if not admin_login_required():
        return redirect(url_for("admin.admin_login"))

    if request.method == "POST":
        title = request.form["title"]
        openings = request.form["openings"]
        position = request.form["position"]
        description = request.form["description"]

        job = Job(
            title=title,
            openings=openings,
            position=position,
            description=description
        )

        db.session.add(job)
        db.session.commit()

        flash("Job added successfully")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/add_job.html")


def _urgent_hiring_ranked_results(form_data):
    title = form_data.get("title", "").strip()
    position = form_data.get("position", "").strip()
    description = form_data.get("description", "").strip()
    top_n = form_data.get("top_n")

    if not title or not position or not description or not isinstance(top_n, int) or top_n < 1:
        return None

    applications = Application.query.order_by(Application.created_at.desc()).all()

    for app in applications:
        app.masked_name = mask_name(app.name)
        app.masked_email = mask_email(app.email)

    virtual_job = SimpleNamespace(
        title=f"{title} ({position})",
        description=description
    )

    ranked_results = rank_applications(virtual_job, applications, top_n)

    for item in ranked_results:
        app = item["application"]
        app.masked_name = mask_name(app.name)
        app.masked_email = mask_email(app.email)

    return ranked_results


@admin_bp.route("/urgent-hiring", methods=["GET", "POST"])
def urgent_hiring():
    if not admin_login_required():
        return redirect(url_for("admin.admin_login"))

    form_data = session.get(
        "urgent_hiring_form",
        {"title": "", "position": "", "description": "", "top_n": 3}
    )
    ranked_results = None

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        position = request.form.get("position", "").strip()
        description = request.form.get("description", "").strip()
        top_n_raw = request.form.get("top_n", "").strip()

        if not title or not position or not description:
            flash("Please fill all urgent hiring fields.")
            form_data = {
                "title": title,
                "position": position,
                "description": description,
                "top_n": top_n_raw or 3
            }
        elif not top_n_raw.isdigit() or int(top_n_raw) < 1:
            flash("Top candidates must be a positive number.")
            form_data = {
                "title": title,
                "position": position,
                "description": description,
                "top_n": top_n_raw
            }
        else:
            form_data = {
                "title": title,
                "position": position,
                "description": description,
                "top_n": int(top_n_raw)
            }
            session["urgent_hiring_form"] = form_data
            ranked_results = _urgent_hiring_ranked_results(form_data)
    else:
        ranked_results = _urgent_hiring_ranked_results(form_data)

    return render_template(
        "admin/urgent_hiring.html",
        form_data=form_data,
        ranked_results=ranked_results
    )


# --------- ADMIN LOGOUT ----------
@admin_bp.route("/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.admin_login"))

# -------- VIEW APPLIED STUDENTS FOR A JOB --------
@admin_bp.route("/applications/<int:job_id>", methods=["GET", "POST"])
def view_applications(job_id):
    if not admin_login_required():
        return redirect(url_for("admin.admin_login"))

    job = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job.id).all()

    for app in applications:
        app.masked_name = mask_name(app.name)
        app.masked_email = mask_email(app.email)
        
    ranked_results = None

    if request.method == "POST":
        top_n = request.form.get("top_n")

        if top_n and top_n.isdigit():
            top_n = int(top_n)
            ranked_results = rank_applications(job, applications, top_n)

            for item in ranked_results:
                app = item["application"]
                app.masked_name = mask_name(app.name)
                app.masked_email = mask_email(app.email)

            # ✅ Store filtered application IDs in session
            filtered_ids = [item["application"].id for item in ranked_results]
            session["filtered_app_ids"] = filtered_ids
            session["current_job_id"] = job.id
            
    return render_template(
        "admin/job_applications.html",
        job=job,
        applications=applications,
        ranked_results=ranked_results
    )

@admin_bp.route("/applications/<int:job_id>/all")
def see_all_applications(job_id):
    if not admin_login_required():
        return redirect(url_for("admin.admin_login"))

    return redirect(url_for("admin.view_applications", job_id=job_id))

@admin_bp.route("/application/<int:app_id>/accept")
def accept_application(app_id):
    if not admin_login_required():
        return redirect(url_for("admin.admin_login"))

    application = Application.query.get_or_404(app_id)

    # Update status
    application.status = "Accepted"
    db.session.commit()

    # Send Email
    send_selection_email(
        application.email,
        application.name,
        application.job.title
    )

    flash("Candidate accepted and email sent.")

    return redirect(url_for("admin.view_applications", job_id=application.job_id))

@admin_bp.route("/application/<int:app_id>/reject")
def reject_application(app_id):
    if not admin_login_required():
        return redirect(url_for("admin.admin_login"))

    application = Application.query.get_or_404(app_id)

    application.status = "Rejected"
    db.session.commit()

    send_rejection_email(
        application.email,
        application.name,
        application.job.title
    )

    return redirect(url_for("admin.view_applications", job_id=application.job_id))


@admin_bp.route("/urgent-hiring/application/<int:app_id>/accept")
def urgent_accept_application(app_id):
    if not admin_login_required():
        return redirect(url_for("admin.admin_login"))

    application = Application.query.get_or_404(app_id)
    application.status = "Accepted"
    db.session.commit()

    send_selection_email(
        application.email,
        application.name,
        application.job.title
    )

    flash("Candidate accepted and email sent.")
    return redirect(url_for("admin.urgent_hiring"))


@admin_bp.route("/urgent-hiring/application/<int:app_id>/reject")
def urgent_reject_application(app_id):
    if not admin_login_required():
        return redirect(url_for("admin.admin_login"))

    application = Application.query.get_or_404(app_id)
    application.status = "Rejected"
    db.session.commit()

    send_rejection_email(
        application.email,
        application.name,
        application.job.title
    )

    flash("Candidate rejected and email sent.")
    return redirect(url_for("admin.urgent_hiring"))

    
@admin_bp.route("/application/<int:app_id>/summary")
def resume_summary(app_id):
    if not admin_login_required():
        return redirect(url_for("admin.admin_login"))

    application = Application.query.get_or_404(app_id)

    # Resume file path (adjust if stored differently)
    resume_path = application.resume  # make sure this stores file path

    try:
        summary_data = analyze_resume(resume_path)
    except Exception as e:
        summary_data = {"error": str(e)}

    return render_template(
        "admin/resume_summary.html",
        application=application,
        summary=summary_data
    )

@admin_bp.route("/applications/<int:job_id>/detailed-analysis", methods=["GET", "POST"])
def detailed_analysis(job_id):
    if not admin_login_required():
        return redirect(url_for("admin.admin_login"))

    # 🔒 Ensure filter was applied
    if "filtered_app_ids" not in session or session.get("current_job_id") != job_id:
        flash("Please filter candidates first.")
        return redirect(url_for("admin.view_applications", job_id=job_id))

    job = Job.query.get_or_404(job_id)

    if request.method == "POST":

        core_skills = request.form.get("core_skills").split(",")
        secondary_skills = request.form.get("secondary_skills").split(",")

        # Clean spaces
        core_skills = [s.strip() for s in core_skills if s.strip()]
        secondary_skills = [s.strip() for s in secondary_skills if s.strip()]

        filtered_ids = session.get("filtered_app_ids")

        applications = Application.query.filter(
            Application.id.in_(filtered_ids)
        ).all()

        results = []

        for app in applications:

            resume_path = app.resume

            try:
                analysis = analyze_resumee(
                    resume_path,
                    job.title,
                    job.description,
                    core_skills,
                    secondary_skills
                )

                results.append({
                    "application": app,
                    "score": analysis["final_score"],
                    "explanation": analysis["explanation"]
                })

            except Exception as e:
                results.append({
                    "application": app,
                    "score": 0,
                    "explanation": f"Error: {str(e)}"
                })

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)

        return render_template(
            "admin/detailed_analysis.html",
            job=job,
            results=results,
            show_results=True
        )

    return render_template(
        "admin/detailed_analysis.html",
        job=job,
        show_results=False
    )




