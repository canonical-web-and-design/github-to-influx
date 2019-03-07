import os

from influxdb import InfluxDBClient

INFLUXDB_CONFIG = {
    "HOST": os.getenv("INFLUXDB_HOST"),
    "PORT": os.getenv("INFLUXDB_PORT"),
    "USERNAME": os.getenv("INFLUXDB_USERNAME"),
    "PASSWORD": os.getenv("INFLUXDB_PASSWORD"),
    "DATABASE": os.getenv("INFLUXDB_DATABASE"),
}

client = InfluxDBClient(
    INFLUXDB_CONFIG["HOST"],
    INFLUXDB_CONFIG["PORT"],
    INFLUXDB_CONFIG["PASSWORD"],
    INFLUXDB_CONFIG["USERNAME"],
    INFLUXDB_CONFIG["DATABASE"],
)

client.create_database(INFLUXDB_CONFIG["DATABASE"])
