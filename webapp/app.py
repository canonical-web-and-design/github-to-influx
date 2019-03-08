import flask
from werkzeug.contrib.fixers import ProxyFix

import talisker.flask
from webapp.providers.github import github

app = flask.Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app)
talisker.flask.register(app)

app.register_blueprint(github, url_prefix="/github")


@app.route("/_status/check")
def check():
    return "OK"
