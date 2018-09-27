import json
import os
from flask import Flask, render_template, request
from TfL_data import get_arrivals_for_station, get_line_status

app = Flask(__name__)

@app.route("/")
def home():
    stations = get_stations()
    return render_template("index.html", stations = stations)

@app.route("/arrivals", methods=["GET"])
def station_arrivals():
    station = request.args.get("station_name")
    tube_stops = station_data()

    for stop in tube_stops:
        if stop["station_name"] == station:
            station_id = stop["station_id"]
            line_id = stop["line_id"]

    line_status = get_line_status(line_id)

    arrivals_info = get_arrivals_for_station(line_id,station_id)
    if len(arrivals_info):
        return render_template("arrivals.html", line_status = line_status, arrivals = arrivals_info)
    else:
        station_info = {"line" : line_id, "station" : station}
        msg = "NO ARRIVALS FOR THIS STATION"
        return render_template("arrivals.html", line_status = line_status, station_info = station_info, msg = msg)

def get_stations():
    tube_stops_list = list()
    tube_stops = station_data()
    for stop in tube_stops:
        #without this check station names get repeated
        if tube_stops_list.count(stop["station_name"]) == 0:
            tube_stops_list.append(stop["station_name"])
    return tube_stops_list

def station_data():
    if os.path.isfile("station_names.json"):
        with open("station_names.json","r") as stations:
            return json.load(stations)

if __name__ == "__main__":
    app.run(debug=True)
