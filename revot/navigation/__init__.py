from flask import Blueprint

navigation = Blueprint('navigation', __name__)

from . import topbar
