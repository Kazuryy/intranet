from flask import Blueprint
messagesbp = Blueprint('messages', __name__)
from . import messages