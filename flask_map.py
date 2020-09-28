#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Generate a html map / frontend for monitor van de stad.
# Based upon:
# https://github.com/python-visualization/folium/issues/958
#

import os
import sys

import glob
import json
import numpy

import branca
import folium

# import geojsoncontour
# import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import scipy as sp
import statistics

from flask import Flask, render_template
from folium.features import DivIcon
from folium import plugins
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

    infile = (sorted(glob.glob('data/knmi*.json'),
                     key=os.path.getmtime)[-1])

    with open(infile, 'r') as fh:
        knmi = json.loads(fh.read())

    return render_template('index.html', data=data, knmi=knmi)


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
    # Load datasource meetjestad, with fallback to older files,
    # in case of corruption
    i = -1
    data1 = False
    while not data1:
        infile = (sorted(glob.glob('data/meetjestad_*.json'),
                  key=os.path.getmtime)[i])
        with open(infile, 'r') as fh:
            try:
                data1 = json.loads(fh.read())
            except Exception:
                i -= 1
                if i < -10:
                    sys.stdout.write("Failed to load KNMI data from:" + infile)
                    sys.exit(-1)

    # Load datasource KNMI, with fallback to older files,
    # in case of corruption
    i = 1
    data2 = False
    while not data2:
        infile = (sorted(glob.glob('data/knmi_*.json'),
                  key=os.path.getmtime)[i])
        with open(infile, 'r') as fh:
            try:
                data2 = json.loads(fh.read())
            except Exception:
                i += 1
                if i > 9:
                    sys.stdout.write("Failed to load KNMI data from:" + infile)
                    sys.exit(-1)

    data = {}
    data.update(data1)
    wanted = ["Eindhoven", "Volkel", "Woensdrecht", "Rotterdam"]

    for item in data2:
        if item not in wanted:
            continue
        data.update({item: data2[item]})

    all_temp = []
    seen = {}
    points = []

    # Extract wanted data from json files
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
        df = pd.DataFrame(points,
                          columns=('latitude',
                                   'longitude',
                                   'temperature'))
    elif map_name == "hum":
        df = pd.DataFrame(points,
                          columns=('latitude',
                                   'longitude',
                                   'humidity'))

    for item in seen:
        all_temp.append(seen[item])

    # Setup
    temp_mean = numpy.mean(all_temp)
    temp_std = statistics.stdev(all_temp)

    # Setup colormap
    colors = [
              '#1b23ba',
              '#2b83ba',
              '#abdda4',
              '#ffffbf',
              '#fdae61',
              '#d7191c',
              '#e2191c',
              '#ff0000',
    ]

    vmin = temp_mean - 2 * temp_std
    vmax = temp_mean + 2 * temp_std
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
    z_mesh = griddata((x_orig, y_orig),
                      z_orig,
                      (x_mesh, y_mesh),
                      method='linear')

    # Gaussian filter the grid to make it smoother
    sigma = [2, 2]
    z_mesh = sp.ndimage.filters.gaussian_filter(z_mesh, sigma, mode='constant')

    '''
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
    '''

    '''
    # Convert matplotlib contourf to geojson
    geojson = geojsoncontour.contourf_to_geojson(
        contourf=contourf,
        min_angle_deg=3.0,
        ndigits=4,
        stroke_width=1,
        fill_opacity=0.3)
    '''

    # Set up the folium plot
    lat = 51.55899230769231
    lon = 5.0862053846153847
    geomap = folium.Map([lat, lon], zoom_start=13, title='mvds')

    '''
    folium.TopoJson(
       json.loads(buurten),
       'test',
       name='topojson'
    ).add_to(geomap)
    '''

    folium.GeoJson('out1.json',
                   style_function=lambda x: {
                    'color': '#222222',
                    'fillColor': '#222222',
                    'opacity': 0.5,
                   }).add_to(geomap)

    # style = {'fillColor': '#ffffff', 'color': '#002200', 'opacity': 0.3}
    folium.GeoJson('out.json',
                   style_function=lambda x: {
                        'color': cm(x['properties']['temp']),
                        'fillColor': cm(x['properties']['temp']),
                        'opacity': 1,
                    }).add_to(geomap)


    '''
    # Plot the contour plot on folium
    folium.GeoJson(
        geojson,
    ).add_to(geomap)
    '''

    # Add measurestations to the map.
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

    # folium.LayerControl().add_to(geomap)

    # Fullscreen mode
    plugins.Fullscreen(position='topright',
                       force_separate_button=True
                       ).add_to(geomap)

    return geomap._repr_html_()


if __name__ == '__main__':
    app.run(debug=True)
