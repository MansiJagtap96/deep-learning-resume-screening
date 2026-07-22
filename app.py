from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models.user import db, User

login_manager = LoginManager()
login_manager.login_view = "auth.login"

import os
os.environ["GEMINI_API_KEY"] = "AIzaSyAc12TvvNs4P-_4lnsbwaR2kHasqR831Ms"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    login_manager.init_app(app)

    # import blueprints INSIDE function
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from models.application import Application
    from routes.user import user_bp
    app.register_blueprint(user_bp)



    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route("/")
    def index():
        return render_template("index.html")

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

