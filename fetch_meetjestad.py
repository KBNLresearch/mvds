#!/usr/bin/env python3

import json
import requests

from datetime import datetime, timedelta
from pprint import pprint
from geopy.geocoders import Nominatim

'''
   Fetch last half hour worth of sensor-data from meetjestad.net.
   Clean it and add street-names to the data.
'''

# Remote uses different timezone
now = datetime.now()
start = now - timedelta(hours=2.5)
end_time = now.strftime("%Y-%m-%d,%H:%M")
start_time = start.strftime("%Y-%m-%d,%H:%M")

URL="https://meetjestad.net/data/?download=1&type=sensors&start=%s&end=%s"
URL1 = "&ids=251%2C264%2C286%2C361%2C369%2C378-380%2C387%2C388%2C403%2C41"
URL1 += "0%2C413%2C416%2C424%2C427%2C430%2C431%2C436%2C437%2C439-441%2C44"
URL1 += "3-446%2C449%2C453%2C456%2C467%2C477%2C478%2C480%2C486%2C488-490%"
URL1 += "2C492-494%2C499%2C500-502%2C504-509%2C560-564%2C568-605%2C607&cmd=download+JSON"

url = URL % (start_time, end_time) + URL1
resp = requests.get(url)

# File with street-names.
with open('locations.json') as fh:
    locations = json.loads(fh.read())

parsed = []
for item in resp.json():
    lat = item.get('latitude')
    lon = item.get('longitude')
    if not lat is None:
        key = str(lat) + "," + str(lon)
        loc = locations.get(key)
        if loc is None:
            geolocator = Nominatim(user_agent="test")
            location = geolocator.reverse(key)
            check = location.address.split(',')[0]
            if check[0].isalnum():
                location_str = location.address.split(',')[1].strip()
            else:
                location_str = location.address.split(',')[0].strip()
            locations[key] = location_str

        parsed.append({'id' : item.get('id'),
                  'lat' : item.get('latitude'),
                  'lon' : item.get('longitude'),
                  'name' : locations[key],
                  'temp' : item.get('temperature'),
                  'hum' : item.get('humidity')})

# Calculate avg temp per sensor station.
json_out = {}
for line in parsed:
    wid = line.pop('id')
    if not wid in json_out:
        json_out[wid] = line
    else:
        print('add')
        line['temp'] += json_out[wid]['temp']
        line['temp'] = line['temp'] / 2
        json_out[wid] = line

pprint(json_out)
print(len(json_out))

# Write out streetnames
with open('locations.json', 'w') as fh:
    fh.write(json.dumps(locations))

# Write out cleaned data
with open("meetjestad.json", "w") as fh:
    fh.write(json.dumps(json_out))
