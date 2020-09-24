import json
import os
import glob

from pprint import pprint

from shapely.geometry import shape, Point
# DEPENDIng on your version, use: from shapely.geometry import shape, Point

# load GeoJSON file containing sectors
with open('wijken.json') as f:
    js = json.load(f)

# construct point based on lon/lat returned by geocoder
infile = (sorted(glob.glob('data/meetjestad_*.json'),
                 key=os.path.getmtime)[-1])

'''

POINT (5.03842 51.55)
{'type': 'Feature', 'geometry':

'''

with open(infile, 'r') as fh:
    data = json.loads(fh.read())


wijken = {}

for item in data:
    #print(data[item])
    try:
        point = Point(data[item].get('lon'), data[item].get('lat'))
    except Exception as e:
        continue
 
    # check each polygon to see if it contains the point
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            wn = feature.get('properties').get('wijknaam')
            if not wn in wijken:
                wijken[wn] = feature
                wijken[wn]['properties']['temp'] = data[item].get('temp')
                wijken[wn]['properties']['fill'] = True
                wijken[wn]['properties']['fillColor'] = '#00ff00'
            else:
                print('here')
                wijken[wn]['properties']['temp'] = (wijken[wn]['properties']['temp'] + data[item].get('temp')) / 2
            continue


new = {'features' : [],  "type" : "FeatureCollection", "name" : "wijken"}

for feature in js['features']:
    wn = feature.get('properties').get('wijknaam')
    if not wn in wijken:
        feature['properties']['fillColor'] = '#aa0000'
        feature['properties']['temp'] = 0
        new['features'].append(feature)

nnew = {'features' : [],  "type" : "FeatureCollection", "name" : "wijken"}

for item in wijken:
    new['features'].append(wijken[item])
    nnew['features'].append(wijken[item])

with open('out.json', 'w') as fh:
    fh.write(json.dumps(nnew))
with open('out1.json', 'w') as fh:
    fh.write(json.dumps(new))
