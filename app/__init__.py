from flask import Flask, render_template
from flask_mail import Mail
from psycopg2 import OperationalError  # For handling PostgreSQL connection errors

mail = Mail()

def create_app():
    app = Flask(__name__)

    # Load configurations (includes your Supabase/PostgreSQL settings)
    app.config.from_object('app.config.Config')

    # Initialize Flask-Mail
    mail.init_app(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.service import service_bp
    from app.routes.project import project_bp
    from app.routes.testimonial import testimonial_bp
    from app.routes.team import team_bp
    from app.routes.auth import auth
    from app.routes.user import user
    from app.routes.admin import admin

    app.register_blueprint(main_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(testimonial_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)

    # ============================
    # 🔴 GLOBAL ERROR HANDLERS
    # ============================

    # Handle custom ConnectionError from database.py
    @app.errorhandler(ConnectionError)
    def handle_connection_error(e):
        return render_template('errors/db_error.html', message=str(e)), 503

    # Handle PostgreSQL OperationalError (Supabase connection issues)
    @app.errorhandler(OperationalError)
    def handle_operational_error(e):
        return render_template(
            'errors/db_error.html',
            message="Database connection failed. Please check your internet or try again later."
        ), 503

    # Handle unexpected internal server errors
    @app.errorhandler(500)
    def handle_internal_error(e):
        return render_template(
            'errors/db_error.html',
            message="An unexpected server error occurred. Please try again later."
        ), 500

    return app
