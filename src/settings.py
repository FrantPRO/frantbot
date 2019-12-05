import os

TOKEN = os.environ.get("TOKEN")
OPENWEATHERMAP_KEY = os.environ.get("OPENWEATHERMAP_KEY")
TIMEZONEDB_KEY = os.environ.get("TIMEZONEDB_KEY")
HOST = os.environ.get("HOST", "0.0.0.0")
NAME = os.environ.get("NAME")
PORT = os.environ.get("PORT", 5000)
