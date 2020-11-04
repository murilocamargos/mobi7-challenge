import pandas as pd
from pathlib import Path
import shutil


def move_files_to_temp_folder(tmp_path, pos=False, poi=False, cons=False):
    org = lambda name: Path(f'./data/{name}.csv')
    tmp = lambda name: tmp_path.joinpath(f'{name}.csv')
    cpy = lambda name: shutil.copy(org(name), tmp(name))
    
    if pos: cpy('posicoes')
    if poi: cpy('base_pois_def')
    if pos: cpy('resultados_consolidado_POIs')


def get_valid_position(n=1):
    positions = [{
        'placa': 'TESTE001',
        'data_posicao': 'Wed Dec 12 2018 00:04:03 GMT-0200 (Hora oficial do Brasil)',
        'velocidade': 0,
        'longitude': -51.469891,
        'latitude': -25.3649141,
        'ignicao': False,
    } for i in range(n)]
    if n == 1:
        return pd.Series(positions[0])
    return pd.DataFrame(positions)


def get_valid_poi(n=1):
    pois = [{
        'nome': 'PONTO 1',
        'raio': 350,
        'latitude': -25.56742701740896,
        'longitude': -51.47653363645077,
    } for i in range(n)]
    if n == 1:
        return pd.Series(pois[0])
    return pd.DataFrame(pois)


def get_poi_pos():
    poi = get_valid_poi(2)
    poi.loc[1, 'latitude'] += 0.004
    poi.loc[1, 'nome'] = 'PONTO 2'
    
    position = get_valid_position(10)
    position.latitude = poi.latitude[0]
    position.longitude = poi.longitude[0]
    mins = 4
    for i in range(1,10):
        mins += 2
        dp = position.loc[i, 'data_posicao']
        position.loc[i, 'latitude'] = position.loc[i-1, 'latitude'] + 0.0008
        position.loc[i, 'data_posicao'] = dp[:19] + str(mins).zfill(2) + dp[21:]
    
    position.loc[2, 'velocidade'] = 10  # Change state to moving
    position.loc[3, 'ignicao'] = True   # Keep moving state
    
    return poi, position