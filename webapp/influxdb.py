import os

from influxdb import InfluxDBClient

INFLUXDB_CONFIG = {
    "HOST": os.getenv("INFLUXDB_HOST"),
    "PORT": os.getenv("INFLUXDB_PORT"),
    "USER": os.getenv("INFLUXDB_USER"),
    "PASSWORD": os.getenv("INFLUXDB_PASSWORD"),
    "DATABASE": os.getenv("INFLUXDB_DATABASE"),
}

client = InfluxDBClient(
    INFLUXDB_CONFIG["HOST"],
    INFLUXDB_CONFIG["PORT"],
    INFLUXDB_CONFIG["USER"],
    INFLUXDB_CONFIG["PASSWORD"],
    INFLUXDB_CONFIG["DATABASE"],
)
