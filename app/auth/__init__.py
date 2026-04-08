from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from . import routes  # noqa: F401, E402
