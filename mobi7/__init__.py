from flask import Flask, current_app
from .blueprint import dash_blueprint
from mobi7.funcs import get_data, feature_eng


def create_app():
    app = Flask(__name__)
    app.register_blueprint(dash_blueprint)

    with app.app_context():
        pos, poi, res = get_data('./data')
        pos = feature_eng(pos.copy(), poi.copy(), add_pois=False)
        current_app.files = (pos, poi, res)
    
    return app
