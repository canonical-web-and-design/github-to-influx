import flask

from webapp.providers import github, usabilla

app = flask.Flask(__name__)
app.register_blueprint(github.build_blueprint(), url_prefix="/github")
app.register_blueprint(usabilla.build_blueprint(), url_prefix="/usabilla")
