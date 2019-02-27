import flask

from webapp.providers.github import build_blueprint

app = flask.Flask(__name__)
app.register_blueprint(build_blueprint(), url_prefix="/github")
