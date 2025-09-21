from flask import Flask
from flask_mysqldb import MySQL #type:ignore
from flask_mail import Mail

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
    

    return app