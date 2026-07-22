from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models.user import User, db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("auth.signup"))

        user = User(
            username=username,
            email=email,
            phone=phone,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash("Signup successful. Please login.")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("user.dashboard"))

        flash("Invalid email or password")

    return render_template("login.html")




@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
