import hmac
import os

import flask

from canonicalwebteam.http import Session
from webapp.influxdb import client

GITHUB_SECRET_KEY = os.getenv("GITHUB_SECRET_KEY")

github = flask.Blueprint("github", __name__)

api_session = Session()


def verify_signature(headers, data, secret):
    header_signature = headers.get("X-Hub-Signature")
    if header_signature is None:
        return False

    sha_name, signature = header_signature.split("=")
    if sha_name != "sha1":
        return False

    mac = hmac.new(bytes(secret.encode()), msg=bytes(data), digestmod="sha1")

    if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
        return False

    return True


def process_response(response):
    if not response.ok:
        raise Exception("Error from api: " + response.status_code)

    return response.json()


@github.route("/", methods=["GET"])
def enabled():
    return "Github webhook is enabled."


@github.route("/webhook", methods=["POST"])
def webhook():
    if not flask.request.json:
        flask.abort(400)

    if not verify_signature(
        headers=flask.request.headers,
        data=flask.request.data,
        secret=GITHUB_SECRET_KEY,
    ):
        flask.abort(401)

    data = flask.request.json
    if "X-Github-Event" in flask.request.headers:
        if flask.request.headers["X-Github-Event"] == "issues":
            fields = {
                "open_issues_count": data["repository"]["open_issues_count"],
                "latest_opened_issue": data["sender"]["login"],
                "latest_title_issue": data["issue"]["title"],
            }

            payload_to_influx(
                measurement="open_issues",
                fields=fields,
                timestamp=data["issue"]["created_at"],
                organisation=data["organization"]["login"],
                project=data["repository"]["name"],
            )
        elif flask.request.headers["X-Github-Event"] == "pull_request":
            if data["action"] in ["opened", "reopened", "closed"]:
                pulls_url = data["repository"]["pulls_url"]

                try:
                    response = api_session.get(pulls_url[:-9])
                    json = process_response(response)

                    fields = {
                        "open_prs_count": len(json),
                        "latest_opened_prs": data["sender"]["login"],
                        "latest_title_prs": data["pull_request"]["title"],
                    }

                    payload_to_influx(
                        measurement="open_prs",
                        fields=fields,
                        timestamp=data["pull_request"]["updated_at"],
                        organisation=data["organization"]["login"],
                        project=data["repository"]["name"],
                    )
                except Exception:
                    pass

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
