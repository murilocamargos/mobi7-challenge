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


app = Flask(__name__)


# Global variables with all the data we need for the dashboard
pos, poi, cons = get_data('./data')
pos = feature_eng(pos, poi, add_pois=False)


@app.route("/")
def index():
    zoom, center = zoom_center(list(poi.longitude.values),
        list(poi.latitude.values))
    return render_template('index.html', pos=pos, poi=poi, zoom=zoom,
        center=center, cons=cons, mapbox_token=os.environ.get("MAPBOX_TOKEN"))


@app.route('/api/total_time')
def api_total_time():
    # Resample the dataframe to get daily aggregated measurements
    df = pos.resample('D', on='data_posicao').sum()
    
    return jsonify({
        'days': [f'{i.month_name()[:3]} {i.day}' for i in df.index],
        'stopped': list((df.tempo_parado.values/60/60).round()),
        'moving': list((df.tempo_andando.values/60/60).round())
    })


@app.route('/api/get_path')
def api_get_path():
    placa = request.args.get('placa')
    df = pos.loc[pos.placa == placa]    
    res = {'latlon': [], 'zoom': 1, 'center': [0, 0]}

    if df.shape[0] > 0:
        df = df.sort_values(by='data_posicao')
        res['latlon'] = df[['latitude', 'longitude']].values.tolist()
    
    res['zoom'], res['center'] = zoom_center(list(df.longitude.values), list(df.latitude.values))

    return jsonify(res)


@app.route('/api/consolidated')
def api_consolidated():
    if cons is None:
        return jsonify(False)

    placa = request.args.get('placa')
    bycar = request.args.get('bycar')

    if placa is not None:
        df = cons[cons.placa == placa]
        res = {
            'poi': list(df.poi.values),
            'parado': list((df.parado.values/60/60).round(2)),
            'total': list((df.total.values/60/60).round(2)),
        }

    elif bycar is not None:
        df = cons.groupby('placa').sum()
        res = {
            'placa': list(df.index.values),
            'parado': list((df.parado.values/60/60).round(2)),
            'total': list((df.total.values/60/60).round(2)),
        }
    
    else:
        df = cons.groupby('poi').sum()
        res = {
            'poi': list(df.index.values),
            'parado': list((df.parado.values/60/60).round(2)),
            'total': list((df.total.values/60/60).round(2)),
        }

    return jsonify(res)


@app.route('/api/check_consolidated')
def api_check_consolidated():
    global cons
    _, _, cons = get_data()
    return jsonify(cons is not None)


@app.route('/api/get_time')
def api_get_time():
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


if __name__ == "__main__":
    if '--consolidate' in sys.argv:
        consolidate_results('./data')
    else:
        app.run(
            host=os.environ.get("BACKEND_HOST", "127.0.0.1"),
            port=5000,
            debug=True,
        )