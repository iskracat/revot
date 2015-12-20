from flask import Blueprint

populate = Blueprint('populate', __name__)

from . import views

