from flask import Flask
import config

#IMPPORT DB
from extensions import db

from .models import user, visitor, visitor_log, task

def create_app():
    # Initialize app
    app = Flask(__name__)

    # APP CONFIG
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

    # INITIALIZE DB
    db.init_app(app)

    # INITIALIZE LOGIN MANAGER

    #REGISTER BLUEPRINTS

    return app