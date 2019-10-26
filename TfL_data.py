import urllib.request as req
import json
import arrow
from operator import itemgetter
from math import floor

# lines list is used to generate station names
lines = ["bakerloo","central","circle","district","hammersmith-city","jubilee",
         "metropolitan","northern","piccadilly","victoria","waterloo-city",
         "tfl-rail","london-overground"]

# brand_colours dict is used to pass correct line branding to views
brand_colours = {"bakerloo" : "#B36305", "central" : "#E32017", "circle" : "#FFD300",
                 "district" : "#00782A", "hammersmith-city" : "#F3A9BB", "metropolitan" : "#9B0056",
                 "northern" : "#000000", "piccadilly" : "#003688", "victoria" : "#0098D4",
                 "waterloo-city" : "#95CDBA", "jubilee" : "#A0A5A9"}

# list to hold all the station names that will present on index view
stations = list()

def expand_station_name(station,lines):
    expanded_names = list()
    for line in lines:
        expanded_name = station.replace("Underground Station","")
        expanded_names.append(expanded_name)
    return expanded_names

def get_stops_for_line(line):
    """create the list of stations that is presented in the index.html view.
        The TFL API includes the phrase 'Underground Station' appended to
        all station names. For the station selection input list this phrase is stripped out"""

    print("Getting stops for {}".format(line))
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
                #check if the station (aka entity) is served by more than one tube line. If so tack on the line to the station name
                if line_mode["modeName"] == "tube" and len(line_mode["lineIdentifier"]) > 1:
                    expanded_station_names = expand_station_name(entity["commonName"],line_mode["lineIdentifier"])
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
        json.dump(stations,destination_file)

def get_arrivals_for_station(line_id,station_id):
    header_info = {}
    platforms = list()
    colour = brand_colours[line_id]

    url = "https://api.tfl.gov.uk/Line/" + line_id + "/Arrivals/" + station_id
    conn = req.urlopen(url)
    data = conn.read()
    str_data = data.decode("utf8")
    train_arrivals = json.loads(str_data)
    sorted_train_arrivals = sorted(train_arrivals, key=itemgetter("timeToStation"))
    if len(train_arrivals):
        current_time = arrow.now('Europe/London').format('HH:mm')
        header_line = train_arrivals[0]["lineName"]
        header_station = train_arrivals[0]["stationName"].replace("Underground Station","")
    else:
        #where API does not return any arrivals for the station return an empty result
        return {},{"line_colour" : colour}

    for train in train_arrivals:
        platforms.append(train['platformName'])

    platform_set = set(platforms)
    available_platforms =  {platform:[] for platform in platform_set}

    """
    for each platform at the station check (for each approaching train)
    which platform the train will arrive at.
    if the platform matches the platform being checked against
    then add the train to the group of arrivals for the platform
    """
    for platform in available_platforms:
        for train in sorted_train_arrivals[:11]:
            if train['platformName'] == platform:
                available_platforms[platform].append({"line" : train['lineName'],
                                                    "station" : train['stationName'],
                                                    "platform" : train['platformName'],
                                                    "towards" : train["towards"],
                                                    "arriving_in" : floor(train["timeToStation"] / 60),
                                                    "time_expected" : arrow.get(train['expectedArrival']).to('Europe/London').format('HH:mm'),
                                                    "currently_at" : train['currentLocation'],
                                                    "arriving_in_secs" : train["timeToStation"],
                                                    "current_time" : current_time})

    header_info["line"] = header_line
    header_info["station"] = header_station
    header_info["line_colour"] = colour

    return available_platforms, header_info

def get_line_status(line_id):
    url = "https://api.tfl.gov.uk/Line/" + line_id + "/Status?detail=true"
    conn = req.urlopen(url)
    data = conn.read()
    str_data = data.decode("utf8")
    json_data = json.loads(str_data)
    line_status = json_data[0]["lineStatuses"][0]["statusSeverityDescription"]
    severity_code = json_data[0]["lineStatuses"][0]["statusSeverity"]
    current_line_status = {"line_status" : line_status, "severity_code" : severity_code}
    return current_line_status

def get_distruption_info(line_id):
    url = "https://api.tfl.gov.uk/Line/" + line_id + "/Disruption"
    conn = req.urlopen(url)
    data = conn.read()
    str_data = data.decode("utf8")
    json_data = json.loads(str_data)

    if json_data:
        return json_data[0]["description"]
    #it maybe there are no distruptions but the API is unable to return arrivals data
    else:
        return """For some reason live arrivals for this station are not available at the moment.
                  Please consult timetables on Transport for London's website."""

def main():
    create_station_data()
    # print(stations)

#can now import this into main.py to use functions but this file will
#not execute as it will not be __main__ unless executing stand-alone
if __name__ == "__main__":
    print("RUNNING")
    main()
