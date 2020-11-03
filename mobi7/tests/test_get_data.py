import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import shutil

from mobi7.funcs import get_data


def move_files_to_temp_folder(tmp_path, pos=False, poi=False, cons=False):
    org = lambda name: Path(f'./data/{name}.csv')
    tmp = lambda name: tmp_path.joinpath(f'{name}.csv')
    cpy = lambda name: shutil.copy(org(name), tmp(name))
    
    if pos: cpy('posicoes')
    if poi: cpy('base_pois_def')
    if pos: cpy('resultados_consolidado_POIs')


def test_get_data_pos_and_poi(tmp_path):
    move_files_to_temp_folder(tmp_path, True, True, True)
    pos, poi, cons = get_data(str(tmp_path.absolute()))
    
    assert type(pos) == pd.core.frame.DataFrame
    assert (pos.columns == ['placa', 'data_posicao', 'velocidade', 'longitude',
        'latitude', 'ignicao']).all()
    
    assert type(poi) == pd.core.frame.DataFrame
    assert (poi.columns == ['nome', 'raio', 'latitude', 'longitude']).all()

    assert type(cons) == pd.core.frame.DataFrame
    assert (cons.columns == ['Unnamed: 0', 'poi', 'total', 'parado',
        'placa']).all()


def test_get_data_dir_not_exists():
    with pytest.raises(NotADirectoryError) as err:
        get_data('./non-existing-dir')
    assert str(err.value) == 'The `dir` must be a directory.'


def test_get_data_pos_file_dont_exist(tmp_path):
    move_files_to_temp_folder(tmp_path, False, True, True)
    path = str(tmp_path.absolute())
    with pytest.raises(FileNotFoundError) as err:
        _, _, _ = get_data(path)
    pos_file = Path(path).joinpath('posicoes.csv')
    full = str(pos_file.absolute())
    assert str(err.value) == f'The positions file `{full}` was not found.'


def test_get_data_poi_file_dont_exist(tmp_path):
    move_files_to_temp_folder(tmp_path, True, False, True)
    path = str(tmp_path.absolute())
    tmp_path.joinpath('posicoes.csv').touch()
    with pytest.raises(FileNotFoundError) as err:
        _, _, _ = get_data(path)
    pos_file = Path(path).joinpath('base_pois_def.csv')
    full = str(pos_file.absolute())
    assert str(err.value) == f'The POIs file `{full}` was not found.'