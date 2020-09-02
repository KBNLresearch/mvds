#!/usr/bin/env python3

import os
import sys
import json
import codecs

from datetime import datetime
from ftplib import FTP
from geopy.geocoders import Nominatim

'''
    Fetch latest data from KNMI.
    Clean it and add lat / lon to the data.
'''

KNMI_FTP = 'ftp.knmi.nl'
KNMI_SRC_DIR = 'pub_weerberichten'
KNMI_SRC_FILE = 'tabel_10Min_data.json'

DATA_DIR = 'data' + os.path.sep

# Cache for location-lookups.
if os.path.isfile('locations.json'):
    with codecs.open('locations.json') as fh:
        locations = json.loads(fh.read())
else:
    locations = {}

# Create datadir if not there.
if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)

ftp = FTP(KNMI_FTP)
ftp.login()

now = datetime.now()
dst_filename = now.strftime("knmi_%Y-%m-%d_%H:%M.json")

ftp.cwd(KNMI_SRC_DIR)
with codecs.open(DATA_DIR + dst_filename, 'wb') as fh:
    ftp.retrbinary('RETR ' + KNMI_SRC_FILE, fh.write)

with codecs.open(DATA_DIR + dst_filename, 'rb') as fh:
    data = json.loads(fh.read())

wanted = ["Eindhoven", "Volkel", "Woensdrecht", "Rotterdam"]

out = {}

for item in data.get('stations'):
    station = item.get('station')

    if not item.get('temperature'):
        continue

    if station not in wanted:
        continue

    out[station] = {}
    out[station]["name"] = station

    out[station]["temp"] = float(item.get('temperature'))
    out[station]["hum"] = float(item.get('humidity'))

    lat = lon = False
    # Use cache for locations.
    for loc, name in locations.items():
        if name == station:
            lat = loc.split(',')[0]
            lon = loc.split(',')[1]

            out[station]["lat"] = float(lat)
            out[station]["lon"] = float(lon)
            break

    # Figure out lat/lon for KNMI-stations.
    if not (lat or lon):
        geolocator = Nominatim()
        location = geolocator.geocode(station)

        if location:
            lat = location.latitude
            lon = location.longitude

            out[station]["lat"] = lat
            out[station]["lon"] = lon
            locations[str(lat) + "," + str(lon)] = station

with open(DATA_DIR + dst_filename, 'w') as fh:
    fh.write(json.dumps(out))

with open('locations.json', 'w') as fh:
    fh.write(json.dumps(locations))
