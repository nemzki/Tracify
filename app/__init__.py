from flask import Flask
import config

from extensions import db, login_manager


def create_app():
    # Initialize app
    app = Flask(__name__)

    # APP CONFIG
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+mysqlconnector://{config.DB_USER}:{config.DB_PASSWORD}'
        f'@{config.DB_HOST}/{config.DB_NAME}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # INITIALIZE DB
    db.init_app(app)

    # INITIALIZE LOGIN MANAGER
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # INITIALIZE CSRF PROTECTION
    # CSRFProtect globally validates all POST requests
    # The context_processor makes csrf_token() callable in every template
    from flask_wtf.csrf import CSRFProtect, generate_csrf
    csrf = CSRFProtect(app)

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    # REGISTER BLUEPRINTS
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.security import security_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(security_bp)

    return app