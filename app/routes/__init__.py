from flask import Blueprint
from . import messages  # noqa: F401,E402


messagesbp = Blueprint('messages', __name__)
