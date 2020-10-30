import os
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
import pandas as pd


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


pos = preprocess_positions_file()
poi = pd.read_csv('data/base_pois_def.csv')


@app.route("/")
def index():
    return render_template('index.html', pos=pos, poi=poi,
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
    res = {'latlon': []}

    if df.shape[0] > 0:
        df = df.sort_values(by='data_posicao')
        res['latlon'] = df[['latitude', 'longitude']].values.tolist()
    
    return jsonify(res)


if __name__ == "__main__":
    app.run(debug=True)