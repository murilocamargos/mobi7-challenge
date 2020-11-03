import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from mobi7.funcs import find_pois
from .helpers import move_files_to_temp_folder


def test_find_pois_type_error():
    with pytest.raises(TypeError) as err:
        find_pois(None, None)
    assert str(err.value) == 'The `measurement` must be a pd.Series.'
    
    with pytest.raises(TypeError) as err:
        find_pois(pd.Series([{'teste': None}]), None)
    assert str(err.value) == 'The `list_of_pois` must be a pd.DataFrame.'


def test_find_pois_value_error():
    with pytest.raises(ValueError) as err:
        find_pois(pd.Series([{'teste': None}]), pd.DataFrame([{'teste': None}]))
    fields = ['placa', 'data_posicao', 'velocidade', 'longitude', 'latitude',
        'ignicao']
    assert str(err.value) == f'The `measurement` series should have the '\
                             f'following fields: {fields}'
    
    measurement = pd.Series({f: None for f in fields})
    with pytest.raises(ValueError) as err:
        find_pois(measurement, pd.DataFrame([{'teste': None}]))
    columns = ['nome', 'raio', 'latitude', 'longitude']
    assert str(err.value) == f'The `list_of_pois` dataframe should have the '\
                             f'following columns: {columns}'