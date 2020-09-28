#!/usr/bin/env python3

import os
import json
import codecs

from datetime import datetime
from ftplib import FTP

'''
    Fetch latest data from KNMI.
    Clean it and add lat / lon to the data.
    Convert placenames to provincenames.
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

place_to_prov = {"Lauwersoog": "Groningen",
                 "Nieuw Beerta": "Groningen",
                 "Terschelling": "Friesland",
                 "Vlieland": "Friesland",
                 "Leeuwarden": "Friesland",
                 "Stavoren": "Friesland",
                 "Eelde": "Drenthe",
                 "Hoogeveen": "Drenthe",
                 "Heino": "Overijssel",
                 "Twente": "Overijssel",
                 "Deelen": "Gelderland",
                 "Hupsel": "Gelderland",
                 "Herwijnen": "Gelderland",
                 "Marknesse": "Flevoland",
                 "Lelystad": "Flevoland",
                 "De Bilt": "Utrecht",
                 "Cabauw": "Utrecht",
                 "Den Helder": "Noord-Holland",
                 "Berkhout": "Noord-Holland",
                 "Schiphol": "Noord-Holland",
                 "Voorschoten": "Zuid-Holland",
                 "Rotterdam": "Zuid-Holland",
                 "Hoek van Holland": "Zuid-Holland",
                 "Wilhelminadorp": "Zeeland",
                 "Vlissingen": "Zeeland",
                 "Westdorpe": "Zeeland",
                 "Woensdrecht": "Noord-Brabant",
                 "Gilze Rijen": "Noord-Brabant",
                 "Volkel": "Noord-Brabant",
                 "Eindhoven": "Noord-Brabant",
                 "Ell": "Limburg",
                 "Arcen": "Limburg",
                 "Maastricht-Aachen Airport": "Limburg",
                 "Wijk aan Zee": "Noord-Holland",
                 }

out = {}

for item in data.get('stations'):
    station = item.get('station')

    if not item.get('temperature'):
        continue

    print(station)

    if station in place_to_prov:
        station = place_to_prov.get(station)

    print(station)

    if station not in out:
        out[station] = {}
        out[station]["name"] = station
        out[station]["temp"] = float(item.get('temperature'))
        out[station]["hum"] = float(item.get('humidity'))
    else:
        out[station]["temp"] = round(((out[station]["temp"] +
                                       float(item.get('temperature'))) / 2), 1)
        out[station]["hum"] = round(((out[station]["hum"] +
                                      float(item.get('humidity'))) / 2), 1)

with open(DATA_DIR + dst_filename, 'w') as fh:
    fh.write(json.dumps(out))
