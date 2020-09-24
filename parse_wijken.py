#!/usr/bin/env python3

import json
import os
import glob

from pprint import pprint

from shapely.geometry import shape, Point

# load GeoJSON file containing sectors
with open('wijken.json') as f:
    wijk_data = json.load(f)

infile = (sorted(glob.glob('data/meetjestad_*.json'),
                 key=os.path.getmtime)[-1])

with open(infile, 'r') as fh:
    mjs_data = json.loads(fh.read())

wijken = {}

for item in mjs_data:
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

        # Add temprature information
        if not wn in wijken:
            wijken[wn] = feature
            wijken[wn]['properties']['temp'] = mjs_data[item].get('temp')
        else:
            wijken[wn]['properties']['temp'] = (wijken[wn]['properties']['temp'] +\
                                                mjs_data[item].get('temp')) / 2

# Create 2 outfiles, 1 contaning all the polygons
# for all neighberhoods, 1 with only temp-info
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
