import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from mobi7.funcs import check_numeric, check_data, POI_FIELDS, POS_FIELDS


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


def test_check_numeric_type():
    position = get_valid_position()
    position.latitude = None
    with pytest.raises(TypeError) as err:
        check_numeric(position.latitude, 'position', check_as='sr')
    assert str(err.value) == 'The `position` field must be numeric.'

    position = get_valid_position(5)
    position.latitude = None
    with pytest.raises(TypeError) as err:
        check_numeric(position.latitude, 'position', check_as='df')
    assert str(err.value) == 'The `position` field must be numeric.'


def test_check_numeric_intv():
    position = get_valid_position()
    position.latitude = 91
    with pytest.raises(ValueError) as err:
        check_numeric(position.latitude, 'position', -90, 90, check_as='sr')
    assert str(err.value) == 'All `position` values must be in [-90,90].'

    position = get_valid_position(5)
    position.loc[2, 'latitude'] = 91
    with pytest.raises(ValueError) as err:
        check_numeric(position.latitude, 'position', -90, 90, check_as='df')
    assert str(err.value) == 'All `position` values must be in [-90,90].'
