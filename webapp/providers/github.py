import hmac
import os

import flask

from webapp.influxdb import client

GITHUB_SECRET_KEY = os.getenv("GITHUB_SECRET_KEY")

github = flask.Blueprint("github", __name__)


def verify_signature():
    header_signature = flask.request.headers.get("X-Hub-Signature")
    if header_signature is None:
        return False

    sha_name, signature = header_signature.split("=")
    if sha_name != "sha1":
        return False

    mac = hmac.new(
        bytes(GITHUB_SECRET_KEY.encode()),
        msg=bytes(flask.request.data),
        digestmod="sha1",
    )

    if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
        return False

    return True


@github.route("/", methods=["GET"])
def enabled():
    return "Github webhook is enabled."


@github.route("/webhook", methods=["POST"])
def webhook():
    if not flask.request.json:
        flask.abort(400)

    if not verify_signature():
        flask.abort(401)

    data = flask.request.json
    print(flask.request.headers)
    if "X-Github-Event" in flask.request.headers:
        if flask.request.headers["X-Github-Event"] == "ping":
            print("I JUST GOT PINGED")
        elif flask.request.headers["X-Github-Event"] == "push":
            print("No. commits in push:", len(data["commits"]))
        elif flask.request.headers["X-Github-Event"] == "issues":

            fields = {
                "open_issues_count": data["repository"]["open_issues_count"],
                "latest_opened_issue": data["sender"]["login"],
                "latest_title_issue": data["issue"]["title"],
            }

            payload_to_influx(
                "open_issues",
                fields,
                data["issue"]["created_at"],
                data["organization"]["login"],
                data["repository"]["name"],
            )

        elif flask.request.headers["X-Github-Event"] == "pull_requests":
            print("PR", data["action"])
            print("No. Commits in PR:", data["pull_request"]["commits"])

    return "", 200


def payload_to_influx(
    measurement, fields, timestamp, organisation, project=None
):
    if not project:
        organisation = project

    json_body = [
        {
            "measurement": measurement,
            "tags": {"organisation": organisation, "project": project},
            "time": timestamp,
            "fields": fields,
        }
    ]

    client.write_points(json_body)
