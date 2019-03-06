import flask

from webapp.providers.github import github
from webapp.providers.usabilla import usabilla

app = flask.Flask(__name__)
app.register_blueprint(github, url_prefix="/github")
app.register_blueprint(usabilla, url_prefix="/usabilla")
