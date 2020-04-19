import json
import os
from flask import Flask, render_template, request
from TfL_data import get_arrivals_for_station, get_line_status, get_distruption_info

app = Flask(__name__)

@app.route("/")
def home():
    stations = get_stations()
    return render_template("index.html", stations = stations)

@app.route("/arrivals", methods=["GET"])
def station_arrivals():
    station = request.args.get("station_name")
    tube_stops = station_data()

    #find the station id (required by API) for which trains arrivals are to be displayed
    for stop in tube_stops:
        if stop["station_name"] == station:
            station_id = stop["station_id"]
            line_id = stop["line_id"]

    line_status = get_line_status(line_id)
    arrivals_info, header_info = get_arrivals_for_station(line_id,station_id)

    """
    some API responses (wrapped up in the dict arrivals_info) contain platforms with no arrivals information
    which would be pointless to display on the UI so the following code removes those platforms (if there are any).
    This seems to affect responses where the line is London Overground and specific stations e.g. Hackney Downs
    so not sure the frequency of this type of response.
    Additionally passing the arrivals_info dict to the UI template with non-exist arrivals was causing the
    application to crash as it expects values to process  
    """
    keys_to_remove = list()
    for key,value in arrivals_info.items():
        if len(value) < 1:
            keys_to_remove.append(key)

    if keys_to_remove:
        for ktr in keys_to_remove:
            arrivals_info.pop(ktr)
    print("keys_to_remove {}".format(keys_to_remove))

    # file = "arrivals_for_single_station.json"
    # with open(file, "w") as out_file:
    #     out_file.write(json.dumps(arrivals_info, indent=4))
    #     out_file.write("\n")
    #     for k,v in arrivals_info.items():
    #         out_file.write(k + str(v) + "\n")
    #         out_file.write("LEN = " + str(len(v)) + "\n")

    if len(arrivals_info):
        return render_template("arrivals.html", line_status = line_status,
                               arrivals = arrivals_info, headers = header_info)
    else:
        #no arrivals have been returned for that station so check for distruptions
        distruption_info = get_distruption_info(line_id)
        header_info["line"] = line_id
        header_info["station"] = station
        msg = "NO ARRIVALS FOR THIS STATION"
        return render_template("arrivals.html", line_status = line_status,
                                headers = header_info, msg = msg, distruption_info=distruption_info)

def get_stations():
    tube_stops_list = list()
    tube_stops = station_data()
    for stop in tube_stops:
        #without this check station names get repeated
        if tube_stops_list.count(stop["station_name"]) == 0:
            tube_stops_list.append(stop["station_name"])
    return tube_stops_list

def station_data():
    if os.path.isfile("station_names_v2.json"):
        with open("station_names_v2.json","r") as stations:
            return json.load(stations)

if __name__ == "__main__":
    app.run(debug=True)
