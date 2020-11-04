from flask import Flask
from .blueprint import dash_blueprint


def create_app():
    app = Flask(__name__)
    app.register_blueprint(dash_blueprint)
    return app
