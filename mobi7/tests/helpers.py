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