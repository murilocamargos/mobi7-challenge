import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from ..funcs import get_data, POS_FIELDS, POI_FIELDS, RES_FIELDS
from .helpers import move_files_to_temp_folder


def test_get_data_pos_and_poi(tmp_path):
    move_files_to_temp_folder(tmp_path, True, True, True)
    pos, poi, cons = get_data(str(tmp_path.absolute()))
    
    assert type(pos) == pd.core.frame.DataFrame
    assert (pos.columns == POS_FIELDS).all()
    
    assert type(poi) == pd.core.frame.DataFrame
    assert (poi.columns == POI_FIELDS).all()

    assert type(cons) == pd.core.frame.DataFrame
    assert (cons.columns == RES_FIELDS).all()


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