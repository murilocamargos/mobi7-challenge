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


def test_check_data_as_check():
    position = get_valid_position()
    with pytest.raises(ValueError) as err:
        check_data(position, 'position', POS_FIELDS, check_as='as')
    assert str(err.value) == 'Please, choose a valid type.'


def test_check_data_types():
    with pytest.raises(TypeError) as err:
        check_data({'teste': 1}, 'position', POS_FIELDS, check_as='sr')
    assert str(err.value) == 'The variable `position` must be a Series.'

    with pytest.raises(TypeError) as err:
        check_data({'teste': 1}, 'position', POS_FIELDS, check_as='df')
    assert str(err.value) == 'The variable `position` must be a DataFrame.'


def test_check_data_removing_fields():
    position = get_valid_position()
    position = position.drop('latitude')
    with pytest.raises(ValueError) as err:
        check_data(position, 'position', POS_FIELDS, check_as='sr')
    assert str(err.value) == 'The `position` Series should have the following '\
                            f'fields: {POS_FIELDS}'

    position = get_valid_position(10)
    position = position.drop('latitude', axis=1)
    with pytest.raises(ValueError) as err:
        check_data(position, 'position', POS_FIELDS, check_as='df')
    assert str(err.value) == 'The `position` DataFrame should have the following '\
                            f'fields: {POS_FIELDS}'


def test_check_data_check_pos_lat_lon():
    position = get_valid_position()
    position.latitude = 91
    with pytest.raises(ValueError) as err:
        check_data(position, 'position', POS_FIELDS, check_as='sr')
    assert str(err.value) == 'All `latitude` values must be in [-90,90].'

    position = get_valid_position(5)
    position.loc[2, 'latitude'] = -91
    with pytest.raises(ValueError) as err:
        check_data(position, 'position', POS_FIELDS, check_as='df')
    assert str(err.value) == 'All `latitude` values must be in [-90,90].'

    position = get_valid_position()
    position.longitude = 181
    with pytest.raises(ValueError) as err:
        check_data(position, 'position', POS_FIELDS, check_as='sr')
    assert str(err.value) == 'All `longitude` values must be in [-180,180].'

    position = get_valid_position(5)
    position.loc[2, 'longitude'] = -181
    with pytest.raises(ValueError) as err:
        check_data(position, 'position', POS_FIELDS, check_as='df')
    assert str(err.value) == 'All `longitude` values must be in [-180,180].'


def test_check_data_check_poi_lat_lon_rad():
    poi = get_valid_poi()
    poi.latitude = 91
    with pytest.raises(ValueError) as err:
        check_data(poi, 'poi', POI_FIELDS, check_as='sr')
    assert str(err.value) == 'All `latitude` values must be in [-90,90].'

    poi = get_valid_poi(5)
    poi.loc[2, 'latitude'] = -91
    with pytest.raises(ValueError) as err:
        check_data(poi, 'poi', POI_FIELDS, check_as='df')
    assert str(err.value) == 'All `latitude` values must be in [-90,90].'

    poi = get_valid_poi()
    poi.longitude = 181
    with pytest.raises(ValueError) as err:
        check_data(poi, 'poi', POI_FIELDS, check_as='sr')
    assert str(err.value) == 'All `longitude` values must be in [-180,180].'

    poi = get_valid_poi(5)
    poi.loc[2, 'longitude'] = -181
    with pytest.raises(ValueError) as err:
        check_data(poi, 'poi', POI_FIELDS, check_as='df')
    assert str(err.value) == 'All `longitude` values must be in [-180,180].'

    poi = get_valid_poi(5)
    poi.loc[2, 'raio'] = -180
    with pytest.raises(ValueError) as err:
        check_data(poi, 'poi', POI_FIELDS, check_as='df')
    assert str(err.value) == 'All `raio` values must be in [0,inf].'