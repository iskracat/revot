from flask import request, current_app
from revot import babel

@babel.localeselector
def get_locale():
    # try to guess the language from the user accept
    # header the browser transmits. The best match wins.
    return request.accept_languages.best_match(current_app.config['LANGUAGES'].keys())

@babel.timezoneselector
def get_timezone():
    return None


