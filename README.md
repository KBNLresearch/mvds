# mvds
Monitor van de stad

Run as follows:
    python3 setup.py install # Install dependencies

These have to run every 1/2 hour:
    ./fetch_knmi.py will create a file in data/knmi-$DATE
    ./fetch_meetjestad.py will create a file in data/meetjestad-$DATE
    ./parse_wijken.py will convert data from meetjestad into local info

This displays the map (http://localhost:5000)
    ./flask_map.py

