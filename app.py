from flask import Flask
from flask import render_template
import pandas as pd


app = Flask(__name__)


@app.route("/")
def index():
    # Le arquivos
    pos = pd.read_csv('data/posicoes.csv')
    # Adiciona feature
    pos['parado'] = (pos.velocidade < 5) & (~pos.ignicao)
    # Converte datas
    pos.data_posicao = pos.data_posicao.apply(lambda x: pd.to_datetime(x[:-25]))
    for placa in pos.placa.unique():
        pos.loc[pos['placa'] == placa] = pos.loc[pos['placa'] == placa].sort_values(by='data_posicao')
        pos.loc[pos['placa'] == placa, 'tempo'] = pos[pos['placa'] == placa].data_posicao.diff().apply(lambda x: x.seconds)
    # Calcula tempo parado e andando
    pos['tempo_parado'] = 0
    pos['tempo_andando'] = 0
    pos.loc[pos.parado,'tempo_parado'] = pos[pos.parado].tempo
    pos.loc[~pos.parado,'tempo_andando'] = pos[~pos.parado].tempo
    df = pos.resample('D', on='data_posicao').sum()
    dias = [f'{i.month_name()[:3]} {i.day}' for i in df.index]
    tempo_parado = list((df.tempo_parado.values/60/60).round())
    tempo_andando = list((df.tempo_andando.values/60/60).round())

    return render_template('index.html', dias=dias, tempo_parado=tempo_parado, tempo_andando=tempo_andando)


if __name__ == "__main__":
    app.run(debug=True)