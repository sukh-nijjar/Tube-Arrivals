import urllib.request as req
import json
from datetime import datetime
from operator import itemgetter

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

# def get_arrivals_for_station(line_id,station_id):
#     arrivals = list()
#     url = "https://api.tfl.gov.uk/Line/" + line_id + "/Arrivals/" + station_id
#     conn = req.urlopen(url)
#     data = conn.read()
#     str_data = data.decode("utf8")
#     json_data = json.loads(str_data) #json_data is a LIST of dicts
#     display_time = json_data[0]["timing"]["sent"][11:16]
#
#     #get next 5 arrivals else results can be too big - introduce pagination next iteration
#     #however looks like the data in not time ordered so I need to sort it
#     for entity in json_data:#[:5]:
#         arrivals.append({"line" : entity['lineName'],
#                         "station" : entity['stationName'],
#                         "platform" : entity['platformName'],
#                         "towards" : entity["towards"],
#                         "arriving_in" : entity["timeToStation"] // 60,
#                         "time_expected" : entity['expectedArrival'][11:16],
#                         "currently_at" : entity['currentLocation'],
#                         "current_time" : display_time})
#     return arrivals
#----------------------------------------------------------------------------
def get_arrivals_for_station(line_id,station_id):
    header_info = {}
    platforms = list()

    url = "https://api.tfl.gov.uk/Line/" + line_id + "/Arrivals/" + station_id
    conn = req.urlopen(url)
    data = conn.read()
    str_data = data.decode("utf8")
    train_arrivals = json.loads(str_data)
    sorted_train_arrivals = sorted(train_arrivals, key=itemgetter("timeToStation"))
    if len(train_arrivals):
        display_time = train_arrivals[0]["timing"]["sent"][11:16]
        header_line = train_arrivals[0]["lineName"]
        header_station = train_arrivals[0]["stationName"]
    else:
        #Becontree solved LOL!!!
        return {},{}

    for train in train_arrivals:
        platforms.append(train['platformName'])

    platform_set = set(platforms)
    available_platforms =  {platform:[] for platform in platform_set}

    #get next 5 arrivals else results can be too big - introduce pagination next iteration
    #however looks like the data in not time ordered so I need to sort it
    """
    for each platform at the station check (for each approaching train)
    which platform the train will arrive/depart from.
    if the departure platform matches the platform being checked against
    then add the train to the group of arrivals for the platform
    """
    for platform in available_platforms:
        for train in sorted_train_arrivals[:10]:
            if train['platformName'] == platform:
                available_platforms[platform].append({"line" : train['lineName'],
                                                    "station" : train['stationName'],
                                                    "platform" : train['platformName'],
                                                    "towards" : train["towards"],
                                                    "arriving_in" : train["timeToStation"] // 60,
                                                    "time_expected" : train['expectedArrival'][11:16],
                                                    "currently_at" : train['currentLocation'],
                                                    "current_time" : display_time})
    header_info["line"] = header_line
    header_info["station"] = header_station
    with open("q.txt", "w+") as out_file:
        out_file.write(json.dumps(available_platforms, indent=4))

    return available_platforms, header_info
#-----------------------------------------------------------------------------------
def get_line_status(line_id):
    url = "https://api.tfl.gov.uk/Line/" + line_id + "/Status?detail=true"
    conn = req.urlopen(url)
    data = conn.read()
    str_data = data.decode("utf8")
    json_data = json.loads(str_data) #json_data is a LIST with a dict...which contains a list LOL!!
    # line_name = json_data[0]["name"]
    line_status = json_data[0]["lineStatuses"][0]["statusSeverityDescription"]
    # current_line_status = {"line_name" : line_name, "line_status" : line_status}
    current_line_status = {"line_status" : line_status}
    return current_line_status

def get_distruption_info(line_id):
    url = "https://api.tfl.gov.uk/Line/" + line_id + "/Disruption"
    conn = req.urlopen(url)
    data = conn.read()
    str_data = data.decode("utf8")
    json_data = json.loads(str_data)
    #it maybe there are no distruptions but the api is unable to return arrivals data
    if json_data:
        return json_data[0]["description"]
    else:
        return """For some reason live arrivals for this station are not available at the moment.
                  Please consult timetables on Transport for London's website."""

def main():
    create_station_data()
    print(stations)
    # for s in stations:
    #     print(s)

#can now import this into main.py to use functions but this file will
#not execute as it will not be __main__ unless executing stand-alone
if __name__ == "__main__":
    main()
