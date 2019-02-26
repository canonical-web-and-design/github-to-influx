import os

import flask

from influxdb import InfluxDBClient

ENDPOINT = "/webhook"
INFLUXDB_CONFIG = {
    "HOST": os.getenv("INFLUXDB_HOST", "influx-db"),
    "PORT": os.getenv("INFLUXDB_PORT", "8086"),
    "USERNAME": os.getenv("INFLUXDB_USERNAME", ""),
    "PASSWORD": os.getenv(
        "INFLUXDB_PASSWORD", ""
    ),
    "DATABASE": os.getenv("INFLUXDB_DATABASE", "githubdb"),
}

client = InfluxDBClient(
    INFLUXDB_CONFIG["HOST"],
    INFLUXDB_CONFIG["PORT"],
    INFLUXDB_CONFIG["PASSWORD"],
    INFLUXDB_CONFIG["USERNAME"],
    INFLUXDB_CONFIG["DATABASE"],
)

client.create_database("githubdb")
app = flask.Flask(__name__)


@app.route(ENDPOINT, methods=["POST"])
def webhook():
    if not flask.request.json:
        flask.abort(400)

    data = flask.request.json
    print(flask.request.headers)
    if "X-Github-Event" in flask.request.headers:
        if flask.request.headers["X-Github-Event"] == "ping":
            payload_to_influx(
               "ping", data, data["organization"]["login"]
            )
            print(
                "Pinged! Webhook created with id {}!".format(
                    data["hook"]["id"]
                )
            )

            result = client.query("select value from ping;")
            print(result)
            print(data)
        elif flask.request.headers["X-Github-Event"] == "push":
            print("No. commits in push:", len(data["commits"]))
        elif flask.request.headers["X-Github-Event"] == "pull_requests":
            print("PR", data["action"])
            print("No. Commits in PR:", data["pull_request"]["commits"])

    return "", 200


def payload_to_influx(measurement, value, organisation, project=None):
    if not project:
        organisation = project

    print(value)
    json_body = [
        {
            "measurement": measurement,
            "tags": {"organisation": organisation, "project": project},
            "time": value["hook"]["created_at"],
            "fields": {"value": value},
        }
    ]

    client.write_points(json_body)
