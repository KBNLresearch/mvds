#!/usr/bin/env python3

import json
import os
import glob

from pprint import pprint

from shapely.geometry import shape, Point


'''
Remap the temprature stations from meetjestad into neighborhood totals.


Source wijken.json
https://ckan.dataplatform.nl/dataset/c8918307-afbf-4c53-b1b8-e2bdf75c5b37/resource/859404dd-fcb3-4017-b83b-77dc2107e1a6/download/wijken.json

Wijken.json contains the polygon per neighborhood.
Given the lat/lon for each station,
calculate the avg. temp per polygon.

Writes out two files, out.json and out1.json.

out.json contains only polygons with temp.
out1.json contains all polygons.

'''

# load GeoJSON file containing sectors
with open('wijken.json') as f:
    wijk_data = json.load(f)

infile = (sorted(glob.glob('data/meetjestad_*.json'),
                 key=os.path.getmtime)[-1])

with open(infile, 'r') as fh:
    mjs_data = json.loads(fh.read())

wijken = {}


# Aggegrate temp/hum data per region.
for item in mjs_data:
    # Try to get the lat/lon,
    # else contine to next dict item.
    try:
        point = Point(mjs_data[item].get('lon'),
                      mjs_data[item].get('lat'))
    except Exception as e:
        continue

    # check each polygon to see if it contains the point
    for feature in wijk_data['features']:
        polygon = shape(feature['geometry'])
        if not polygon.contains(point):
            continue

        wn = feature.get('properties').get('wijknaam')

        # Add temprature information to polygon
        if wn not in wijken:
            wijken[wn] = feature
            wijken[wn]['properties']['temp'] = mjs_data[item].get('temp')
            wijken[wn]['properties']['hum'] = mjs_data[item].get('hum')
        else:
            temp = wijken[wn]['properties']['temp']
            hum = wijken[wn]['properties']['hum']
            wijken[wn]['properties']['temp'] = (temp +
                                                mjs_data[item].get('temp')) / 2
            wijken[wn]['properties']['hum'] = (hum +
                                               mjs_data[item].get('hum')) / 2

# Create two outfiles, one contaning all the polygons
# for all neighborhoods, one with only temp-info
new = {'features': [],
       'type': 'FeatureCollection',
       'name': 'wijken'}

for feature in wijk_data['features']:
    wn = feature.get('properties').get('wijknaam')
    if wn not in wijken:
        feature['properties']['temp'] = 0
        new['features'].append(feature)

nnew = {'features': [],
        'type': 'FeatureCollection',
        'name': 'wijken'}

for item in wijken:
    new['features'].append(wijken[item])
    nnew['features'].append(wijken[item])

with open('out.json', 'w') as fh:
    fh.write(json.dumps(nnew))

with open('out1.json', 'w') as fh:
    fh.write(json.dumps(new))
