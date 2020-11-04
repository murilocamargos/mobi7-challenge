"""
The dashboard Blueprint.
"""
from flask import Blueprint
dash_blueprint = Blueprint('dash', __name__, template_folder='templates')

import mobi7.routes
