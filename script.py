from __future__ import print_function

import os
from wsgiref.simple_server import make_server

from influxdb import InfluxDBClient
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

ENDPOINT = "webhook"
INFLUXDB_CONFIG = {
    "HOST": os.getenv("INFLUXDB_HOST", "localhost"),
    "PORT": os.getenv("INFLUXDB_PORT", "8086"),
    "USERNAME": os.getenv("INFLUXDB_USERNAME", ""),
    "PASSWORD": os.getenv("INFLUXDB_PASSWORD", ""),
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


def payload_to_influx(measurement, value, organisation, project=None):
    if not project:
        organisation = project

    json_body = [
        {
            "measurement": measurement,
            "tags": {"organisation": organisation, "project": project},
            "time": value["hook"]["created_at"],
            "fields": {"value": value},
        }
    ]

    client.write_points(json_body)


@view_defaults(route_name=ENDPOINT, renderer="json", request_method="POST")
class PayloadView(object):
    def __init__(self, request):
        self.request = request
        self.payload = self.request.json

    @view_config(header="X-Github-Event:push")
    def payload_push(self):
        print("No. commits in push:", len(self.payload["commits"]))
        return Response("success")

    @view_config(header="X-Github-Event:pull_request")
    def payload_pull_request(self):
        print("PR", self.payload["action"])
        print("No. Commits in PR:", self.payload["pull_request"]["commits"])

        return Response("success")

    @view_config(header="X-Github-Event:ping")
    def payload_else(self):
        payload_to_influx(
            "ping", self.payload, self.payload["organization"]["login"]
        )
        print(
            "Pinged! Webhook created with id {}!".format(
                self.payload["hook"]["id"]
            )
        )

        result = client.query("select value from ping;")
        print("Result: {0}".format(result))
        return {"status": 200}


if __name__ == "__main__":
    config = Configurator()

    config.add_route(ENDPOINT, "/{}".format(ENDPOINT))
    config.scan()

    app = config.make_wsgi_app()
    server = make_server("0.0.0.0", 8000, app)

    server.serve_forever()
