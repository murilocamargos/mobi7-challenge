import os
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
import pandas as pd
import numpy as np


app = Flask(__name__)


def preprocess_positions_file():
    # Get data from database or CSV file
    pos = pd.read_csv('data/posicoes.csv')
    # Add column to identify stopped vehicles
    pos['parado'] = (pos.velocidade < 5) & (~pos.ignicao)
    # Convert all date strings to datetime
    pos.data_posicao = pos.data_posicao.apply(lambda x: pd.to_datetime(x[:-25]))
    # Compute the ellapsed time between measurements for each vehicle
    for placa in pos.placa.unique():
        pos.loc[pos['placa'] == placa] = pos.loc[pos['placa'] == placa].\
            sort_values(by='data_posicao')
        pos.loc[pos['placa'] == placa, 'tempo'] = pos[pos['placa'] == placa].\
            data_posicao.diff().apply(lambda x: x.seconds)
    # Compute stopped and moving times
    pos['tempo_parado'] = 0
    pos['tempo_andando'] = 0
    pos.loc[pos.parado, 'tempo_parado'] = pos[pos.parado].tempo
    pos.loc[~pos.parado, 'tempo_andando'] = pos[~pos.parado].tempo
    
    return pos


def zoom_center(lons: tuple=None, lats: tuple=None, lonlats: tuple=None,
        format: str='lonlat', projection: str='mercator',
        width_to_height: float=2.0) -> (float, dict):
    """Finds optimal zoom and centering for a plotly mapbox.
    Must be passed (lons & lats) or lonlats.
    Temporary solution awaiting official implementation, see:
    https://github.com/plotly/plotly.js/issues/3434
    https://stackoverflow.com/questions/63787612/plotly-automatic-zooming-for-mapbox-maps
    
    Parameters
    --------
    lons: tuple, optional, longitude component of each location
    lats: tuple, optional, latitude component of each location
    lonlats: tuple, optional, gps locations
    format: str, specifying the order of longitud and latitude dimensions,
        expected values: 'lonlat' or 'latlon', only used if passed lonlats
    projection: str, only accepting 'mercator' at the moment,
        raises `NotImplementedError` if other is passed
    width_to_height: float, expected ratio of final graph's with to height,
        used to select the constrained axis.
    
    Returns
    --------
    zoom: float, from 1 to 20
    center: dict, gps position with 'lon' and 'lat' keys

    >>> print(zoom_center((-109.031387, -103.385460),
    ...     (25.587101, 31.784620)))
    (5.75, {'lon': -106.208423, 'lat': 28.685861})
    """
    if lons is None and lats is None:
        if isinstance(lonlats, tuple):
            lons, lats = zip(*lonlats)
        else:
            raise ValueError(
                'Must pass lons & lats or lonlats'
            )
    
    maxlon, minlon = max(lons), min(lons)
    maxlat, minlat = max(lats), min(lats)
    center = [round((maxlat + minlat) / 2, 6), round((maxlon + minlon) / 2, 6)]
    
    # longitudinal range by zoom level (20 to 1)
    # in degrees, if centered at equator
    lon_zoom_range = np.array([
        0.0007, 0.0014, 0.003, 0.006, 0.012, 0.024, 0.048, 0.096,
        0.192, 0.3712, 0.768, 1.536, 3.072, 6.144, 11.8784, 23.7568,
        47.5136, 98.304, 190.0544, 360.0
    ])
    
    if projection == 'mercator':
        margin = 2
        height = (maxlat - minlat) * margin * width_to_height
        width = (maxlon - minlon) * margin
        lon_zoom = np.interp(width , lon_zoom_range, range(20, 0, -1))
        lat_zoom = np.interp(height, lon_zoom_range, range(20, 0, -1))
        zoom = round(min(lon_zoom, lat_zoom), 2)
    else:
        raise NotImplementedError(
            f'{projection} projection is not implemented'
        )
    
    return zoom, center


pos = preprocess_positions_file()
poi = pd.read_csv('data/base_pois_def.csv')


@app.route("/")
def index():
    zoom, center = zoom_center(list(poi.longitude.values), list(poi.latitude.values))
    return render_template('index.html', pos=pos, poi=poi, zoom=zoom, center=center,
        mapbox_token=os.environ.get("MAPBOX_TOKEN"))


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