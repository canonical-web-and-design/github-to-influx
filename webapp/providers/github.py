import flask
from webapp.influxdb import client


def build_blueprint():

    github = flask.Blueprint("github", __name__)

    @github.route("/", methods=["GET"])
    def enabled():
        return "Github webhook is enabled."

    @github.route("/webhook", methods=["POST"])
    def webhook():
        if not flask.request.json:
            flask.abort(400)

        data = flask.request.json
        print(flask.request.headers)
        if "X-Github-Event" in flask.request.headers:
            if flask.request.headers["X-Github-Event"] == "ping":
                print("I JUST GOT PINGED")
            elif flask.request.headers["X-Github-Event"] == "push":
                print("No. commits in push:", len(data["commits"]))
            elif flask.request.headers["X-Github-Event"] == "issues":

                fields = {
                    "open_issues_count": data["repository"][
                        "open_issues_count"
                    ],
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

    return github
