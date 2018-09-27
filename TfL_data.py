import urllib.request as req
import json

lines = ["bakerloo","central","circle","district","hammersmith-city","jubilee",
         "metropolitan","northern","piccadilly","victoria","waterloo-city",
         "tfl-rail","london-overground"]

stations = list()

def expand_station_name(station,lines):
    expanded_names = list()
    for line in lines:
        expanded_name = station.replace("Underground Station","") #+ "- " + line.capitalize() + " Line"
        # if stations.count()
        expanded_names.append(expanded_name)
    return expanded_names

def get_stops_for_line(line):
    """create the list of stations that is presented in the index.html viewself.
        The TFL API includes the phrase 'Underground Station' appended to
        all station names. For the station selection input list this is stripped out"""
    line_stations = list()

    #set the url for API call
    url = "https://api.tfl.gov.uk/Line/" + line + "/StopPoints"
    #open url
    connection = req.urlopen(url)
    #read url (connection is automatically closed after read())
    # and decode data read as it is returned as bytes
    line_station_data = connection.read().decode("utf8")
    #parse line_data into Python data structure
    json_data = json.loads(line_station_data)

    for entity in json_data:
        if "tube" in entity["modes"]:
            for line_mode in entity["lineModeGroups"]:
                #check if the station (aka entity) is served by more than one tube line
                if line_mode["modeName"] == "tube" and len(line_mode["lineIdentifier"]) > 1:
                    expanded_station_names = expand_station_name(entity["commonName"],line_mode["lineIdentifier"])
                    # print("returned list = {}".format(expanded_station_names))
                    for expanded_station_name in expanded_station_names:
                        station_data = {}
                        station_data["station_name"] = expanded_station_name + "- " + line.capitalize() + " Line"
                        station_data["station_id"] = entity["naptanId"]
                        station_data["line_id"] = line
                        line_stations.append(station_data)
                elif line_mode["modeName"] == "tube" and len(line_mode["lineIdentifier"]) == 1:
                    station_data = {}
                    station_data["station_name"] = entity["commonName"].replace("Underground Station","")
                    station_data["station_id"] = entity["naptanId"]
                    station_data["line_id"] = line
                    line_stations.append(station_data)

        # line_stations.append(entity["commonName"])
        # line_stations.append([entity["commonName"],entity["naptanId"]])

    stations.extend(line_stations)

def create_station_data():
    """it is expensive and wasteful to call TfL api to get
       station names every time index view loads. This methods
       writes the station data to a file which then serves as
       the source data for the station search on the index view"""

    file = "station_names.json"

    for line in lines:
        get_stops_for_line(line)

    with open(file, "w") as destination_file:
        # destination_file.write(json.dumps(stations))
        json.dump(stations,destination_file)

def get_arrivals_for_station(line_id,station_id):
    arrivals = list()
    url = "https://api.tfl.gov.uk/Line/" + line_id + "/Arrivals/" + station_id
    conn = req.urlopen(url)
    data = conn.read()
    str_data = data.decode("utf8")
    json_data = json.loads(str_data) #json_data is a LIST of dicts

    for entity in json_data:
        arrivals.append({"line" : entity['lineName'],
                         "station" : entity['stationName'],
                         "platform" : entity['platformName'],
                         "towards" : entity["towards"],
                         "arriving_in" : entity["timeToStation"],
                         "time_expected" : entity['expectedArrival'],
                         "currently_at" : entity['currentLocation']})
    return arrivals

def get_line_status(line_id):
    url = "https://api.tfl.gov.uk/Line/" + line_id + "/Status?detail=true"
    conn = req.urlopen(url)
    data = conn.read()
    str_data = data.decode("utf8")
    json_data = json.loads(str_data) #json_data is a LIST with a dict...which contains a list LOL!!
    return json_data[0]["lineStatuses"][0]["statusSeverityDescription"]
    # for entity in json_data:
    #     print("entity keys are {}".format(entity.items()))
    #     print("lineStatuses is TYPE {}".format(type(entity["lineStatuses"])))
    #     line_state = entity["lineStatuses"][0]["statusSeverityDescription"]

def main():
    create_station_data()
    print(stations)
    # for s in stations:
    #     print(s)

#can now import this into main.py to use functions but this file will
#not execute as it will not be __main__ unless executing stand-alone
if __name__ == "__main__":
    main()
