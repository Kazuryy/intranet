from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from .. import limiter  # noqa: E402
limiter.limit("60 per minute")(admin_bp)

from . import routes  # noqa: F401, E402
