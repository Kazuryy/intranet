from flask import Blueprint

edt_bp = Blueprint('edt', __name__)

from . import routes  # noqa: F401, E402
