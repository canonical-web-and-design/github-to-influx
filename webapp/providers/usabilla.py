import time
from time import mktime
from datetime import datetime

import flask
from webapp.influxdb import client


def build_blueprint():

    usabilla = flask.Blueprint("usabilla", __name__)
    client.create_database("usabilladb")

    @usabilla.route("/", methods=["GET"])
    def enabled():
        return "Usabilla webhook is enabled."

    @usabilla.route("/webhook", methods=["POST"])
    def webhook():
        if not flask.request.json:
            flask.abort(400)

        data = flask.request.json

        url = data.get("url")
        rating = data.get("rating")
        creation_date = data.get("creation_date")

        if creation_date and rating and url:
            s_since_epoch = int(data.get("creation_date").rsplit(" ")[1])
            dt = datetime.utcfromtimestamp(s_since_epoch).isoformat()
            fields = {"url": url, "rating": rating}
            payload = payload_to_influx("rating", fields, dt)
            client.write_points(payload)
        return "", 200

    def payload_to_influx(measurement, fields, timestamp):
        return [{"measurement": measurement, "time": timestamp, "fields": fields}]

    return usabilla
