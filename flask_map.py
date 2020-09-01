#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import json
import numpy
import glob

import branca
import folium
import geojsoncontour
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as sp
import scipy.ndimage
import statistics

from flask import Flask, render_template
from folium.features import DivIcon
from folium import plugins
from pprint import pprint
from scipy.interpolate import griddata

app = Flask(__name__)


@app.route('/')
def index():
    # The index renders the landings-page.
    # Stylesheets in templates/
    infile = (sorted(glob.glob('data/meetjestad_*.json'),
                     key=os.path.getmtime)[-1])

    with open(infile, 'r') as fh:
        data = json.loads(fh.read())

    return render_template('index.html', data=data)

@app.route('/hum.html')
def hum():
    # The index renders the landings-page.
    # Stylesheets in templates/
    infile = (sorted(glob.glob('data/meetjestad_*.json'),
                     key=os.path.getmtime)[-1])

    with open(infile, 'r') as fh:
        data = json.loads(fh.read())

    return render_template('hum.html', data=data)



@app.route('/temp_map.html')
def temp_map():
    return map()

@app.route('/hum_map.html')
def hum_map():
    return map("hum")


def map(map_name="temp"):
    infile = (sorted(glob.glob('data/meetjestad_*.json'),
                     key=os.path.getmtime)[-1])
    # infile = "data/meetjestad_2020-08-25_13:46.json"
    with open(infile, 'r') as fh:
        data1 = json.loads(fh.read())

    infile = (sorted(glob.glob('data/knmi_*.json'), key=os.path.getmtime)[-1])
    with open(infile, 'r') as fh:
        data2 = json.loads(fh.read())

    #data2 = {}
    data = {}
    data.update(data1)
    data.update(data2)

    all_temp = []
    seen = {}
    points = []

    for item in data:
        try:
            lat = data.get(item).get('lat')
        except Exception:
            continue

        lon = data.get(item).get('lon')
        if map_name == "temp":
            temp = round(data.get(item).get('temp'), 2)
        elif map_name == "hum":
            hum = round(data.get(item).get('hum'), 2)

        if lat and lon:
            key = str(lat) + str(lon)
            if not seen.get(key):
                if map_name == "temp":
                    seen[key] = round(temp, 2)
                    points.append([lat, lon, round(temp, 2)])
                elif map_name == "hum":
                    seen[key] = round(hum, 2)
                    points.append([lat, lon, round(hum, 2)])

    if map_name == "temp":
        df = pd.DataFrame(points, columns=('latitude', 'longitude', 'temperature'))
    elif map_name == "hum":
        df = pd.DataFrame(points, columns=('latitude', 'longitude', 'humidity'))

    for item in seen:
        all_temp.append(seen[item])

    # Setup
    temp_mean = numpy.mean(all_temp)
    temp_std = statistics.stdev(all_temp)
    debug = False

    # Setup colormap
    '''
    colors = [
              '#1b23ba',
              '#2b83ba',
              '#abdda4',
              '#ffffbf',
              '#fdae61',
              '#d7191c',
              '#e2191c',
              '#ff0000'
    ]
    '''

    colors = []
    def rgb_to_hex(rgb):
        return '#%02x%02x%02x' % rgb

    for i in range(0,255,int(255 / 7)):
        colors.append(rgb_to_hex((i, 0 , 255-i)))

    vmin = temp_mean - 2.5 * temp_std
    vmax = temp_mean + 2.5 * temp_std
    levels = len(colors)
    cm = branca.colormap.LinearColormap(colors,
                                        vmin=vmin,
                                        vmax=vmax).to_step(levels)

    # The original data
    x_orig = np.asarray(df.longitude.tolist())
    y_orig = np.asarray(df.latitude.tolist())

    if map_name == "temp":
        z_orig = np.asarray(df.temperature.tolist())
    elif map_name == "hum":
        z_orig = np.asarray(df.humidity.tolist())

    # Make a grid
    x_arr = np.linspace(np.min(x_orig), np.max(x_orig), 1500)
    y_arr = np.linspace(np.min(y_orig), np.max(y_orig), 1500)
    x_mesh, y_mesh = np.meshgrid(x_arr, y_arr)

    # Grid the values
    z_mesh = griddata((x_orig, y_orig), z_orig, (x_mesh, y_mesh), method='linear')

    # Gaussian filter the grid to make it smoother
    sigma = [2, 2]
    z_mesh = sp.ndimage.filters.gaussian_filter(z_mesh, sigma, mode='constant')

    # Create the contour
    contourf = plt.contourf(x_mesh,
                            y_mesh,
                            z_mesh,
                            levels,
                            alpha=0.8,
                            colors=colors,
                            linestyles='None',
                            vmin=vmin,
                            vmax=vmax)

    # Convert matplotlib contourf to geojson
    geojson = geojsoncontour.contourf_to_geojson(
        contourf=contourf,
        min_angle_deg=3.0,
        ndigits=4,
        stroke_width=1,
        fill_opacity=0.3)

    # Set up the folium plot
    lat = 51.55899230769231
    lon = 5.0862053846153847
    geomap = folium.Map([lat, lon], zoom_start=13, tiles="cartodbpositron")

    # Plot the contour plot on folium
    folium.GeoJson(
        geojson,
        style_function=lambda x: {
            'color': x['properties']['stroke'],
            'weight': x['properties']['stroke-width'],
            'fillColor': x['properties']['fill'],
            'opacity': 0.5,
        }).add_to(geomap)


    for p in points:
        lat = p[0]
        lon = p[1]
        temp = str(round(seen[str(lat) + str(lon)], 2))
        folium.map.Marker([lat, lon],
                          icon=DivIcon(
                            icon_size=(150, 36),
                            icon_anchor=(0, 0),
                            html='<div style="font-size: 15pt">'
                                 + temp + '</div>',)
                          ).add_to(geomap)


    # Add the colormap to the folium map
    if map_name == "temp":
        cm.caption = 'Temperatuur'
    elif map_name == "humidity":
        cm.caption = 'Luchtvochtigheid'

    geomap.add_child(cm)

    # Fullscreen mode
    plugins.Fullscreen(position='topright',
                       force_separate_button=True
                       ).add_to(geomap)

    return geomap._repr_html_()


if __name__ == '__main__':
    app.run(debug=True)
