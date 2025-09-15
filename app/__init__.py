from flask import Flask

from app.config import Config

def create_app():
    app = Flask(__name__)

    # Load configuration from config.py
    app.config.from_object(Config)



    # Register only the blueprints you're currently working with
    from app.routes.main import main_bp
    from app.routes.auth import auth
    from app.routes.service import service_bp
    from app.routes.project import project_bp
    from app.routes.testimonial import testimonial_bp
    from app.routes.team import team_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth)
    app.register_blueprint(service_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(testimonial_bp)
    app.register_blueprint(team_bp)

    return app
