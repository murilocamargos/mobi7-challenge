import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from mobi7.funcs import find_pois, POI_FIELDS, POS_FIELDS
from .helpers import move_files_to_temp_folder


def get_valid_measurement():
    measurement = {
        'placa': 'TESTE001',
        'data_posicao': 'Wed Dec 12 2018 00:04:03 GMT-0200 (Hora oficial do Brasil)',
        'velocidade': 0,
        'longitude': -51.469891,
        'latitude': -25.3649141,
        'ignicao': False,
    }
    return pd.Series(measurement)


def test_find_pois_type_error():
    with pytest.raises(TypeError) as err:
        find_pois(None, None)
    assert str(err.value) == 'The variable `measurement` must be a Series.'
    
    measurement = get_valid_measurement()
    with pytest.raises(TypeError) as err:
        find_pois(measurement, None)
    assert str(err.value) == 'The variable `list_of_pois` must be a DataFrame.'


def test_find_pois_value_error():
    with pytest.raises(ValueError) as err:
        find_pois(pd.Series([{'teste': None}]), pd.DataFrame([{'teste': None}]))
    assert str(err.value) == f'The `measurement` Series should have the '\
                             f'following fields: {POS_FIELDS}'
    
    measurement = get_valid_measurement()
    with pytest.raises(ValueError) as err:
        find_pois(measurement, pd.DataFrame([{'teste': None}]))
    assert str(err.value) == f'The `list_of_pois` DataFrame should have the '\
                             f'following fields: {POI_FIELDS}'