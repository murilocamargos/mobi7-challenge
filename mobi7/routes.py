import os
import sys
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
import pandas as pd
import numpy as np
from mobi7.funcs import get_data, feature_eng, consolidate_results
from mobi7.utils import zoom_center
from mobi7.blueprint import dash_blueprint


# Global variables with all the data we need for the dashboard
def get_dash_data(feat_eng=True):
    pos, poi, cons = get_data('./data')
    if feat_eng:
        pos = feature_eng(pos, poi, add_pois=False)
    return pos, poi, cons


@dash_blueprint.route("/")
def index():
    """
    Renders the dashboard's initial page with the positions table, the POIs
    table, the best zoom and center for all POIs, and the MapBox API token.
    """
    pos, poi, cons = get_dash_data()
    zoom, center = zoom_center(list(poi.longitude.values),
        list(poi.latitude.values))
    return render_template('index.html', pos=pos, poi=poi, zoom=zoom,
        center=center, cons=cons, mapbox_token=os.environ.get("MAPBOX_TOKEN"))


@dash_blueprint.route('/api/get_path')
def api_get_path():
    """
    API endpoint to obtain the full route by vehicle. Also finds the best zoom
    and center to display the route.
    """
    pos, _, _ = get_dash_data()
    placa = request.args.get('placa')
    df = pos.loc[pos.placa == placa]

    if df.shape[0] == 0:
        return jsonify({'error': 'Car not found.'}), 404

    res = {'latlon': [], 'zoom': 1, 'center': [0, 0]}

    df = df.sort_values(by='data_posicao')
    res['latlon'] = df[['latitude', 'longitude']].values.tolist()
    
    res['zoom'], res['center'] = zoom_center(list(df.longitude.values), list(df.latitude.values))

    return jsonify(res)


@dash_blueprint.route('/api/consolidated')
def api_consolidated():
    """
    API endpoint to get consolidated results to reach the functional
    requirements.
    """
    _, _, cons = get_dash_data()
    if cons is None:
        return jsonify(False)

    placa = request.args.get('placa')
    bycar = request.args.get('bycar')

    if placa is not None:
        # Total and stopped time spent in each POI for a given vehicle
        df = cons[cons.placa == placa]
        res = {
            'poi': list(df.poi.values),
            'parado': list((df.parado.values/60/60).round(2)),
            'total': list((df.total.values/60/60).round(2)),
        }

    elif bycar is not None:
        # Total and stopped time spent in each POI aggregated by the vehicles
        df = cons.groupby('placa').sum()
        res = {
            'placa': list(df.index.values),
            'parado': list((df.parado.values/60/60).round(2)),
            'total': list((df.total.values/60/60).round(2)),
        }
    
    else:
        # Total and stopped time spent by each vehicle aggregated by the POIs
        df = cons.groupby('poi').sum()
        res = {
            'poi': list(df.index.values),
            'parado': list((df.parado.values/60/60).round(2)),
            'total': list((df.total.values/60/60).round(2)),
        }

    return jsonify(res)


@dash_blueprint.route('/api/check_consolidated')
def api_check_consolidated():
    """
    API endpoint to check if the consolidated CSV file exists. If it exists,
    load it to a global variable.
    """
    _, _, cons = get_dash_data(False)
    return jsonify(cons is not None)


@dash_blueprint.route('/api/get_time')
def api_get_time():
    """
    API endpoint to get the total and stopped time spent by each vehicle in a
    POIs selected by the user in real-time.
    """
    pos, poi, cons = get_dash_data()
    params = {
        'lat': request.args.get('lat'),
        'lon': request.args.get('lon'),
        'rad': request.args.get('rad'),
    }

    for p in params:
        try:
            params[p] = float(params[p])
        except:
            return jsonify({'error': f'The `{p}` argument must be numeric.'})

    poi = pd.DataFrame([{'nome': 'POI Escolhido', 'raio': params['rad'],\
        'latitude': params['lat'], 'longitude': params['lon']}])

    cons = consolidate_results(provided_poi=poi, save_file=False)
    cons = cons.loc[cons.poi == 'POI Escolhido']

    df = cons.groupby('placa').sum()
    res = {
        'placa': list(df.index.values),
        'parado': list((df.parado.values/60/60).round(2)),
        'total': list((df.total.values/60/60).round(2)),
    }

    return jsonify(res)
