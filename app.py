import os
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
import pandas as pd
import numpy as np
from consolidate import get_data, feature_eng
from utils import zoom_center


app = Flask(__name__)


# Global variables with all the data we need for the dashboard
pos, poi, cons = get_data()
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


if __name__ == "__main__":
    app.run(debug=True)