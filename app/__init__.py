from flask import Flask, render_template
from flask_mysqldb import MySQL  # type:ignore
from flask_mail import Mail
from psycopg2 import OperationalError  # if you're using psycopg2 in database.py

mysql = MySQL()
mail = Mail()

def create_app():
    app = Flask(__name__)

    # Load configurations
    app.config.from_object('app.config.Config')

    # Initialize extensions
    mysql.init_app(app)
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

    # Handles your raised ConnectionError from database.py
    @app.errorhandler(ConnectionError)
    def handle_connection_error(e):
        return render_template('errors/db_error.html', message=str(e)), 503

    # Handles psycopg2 or MySQL operational failures (optional safety net)
    @app.errorhandler(OperationalError)
    def handle_operational_error(e):
        return render_template('errors/db_error.html', message="Database connection failed. Please try again later."), 503

    # Handles any other unexpected server errors
    @app.errorhandler(500)
    def handle_internal_error(e):
        return render_template('errors/db_error.html', message="An unexpected error occurred. Please try again later."), 500

    return app
