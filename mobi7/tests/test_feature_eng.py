import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from ..funcs import feature_eng, POS_FIELDS
from .helpers import get_valid_position, get_valid_poi, get_poi_pos


@pytest.mark.run(order=13)
def test_feature_eng_columns():
    poi, pos = get_poi_pos()
    pos = feature_eng(pos, poi, add_pois=True)
    POS_FIELDS_ALT = POS_FIELDS + ['parado', 'tempo_parado', 'tempo_andando',
        'POIs', 'tempo']
    assert len(set(pos.columns).difference(set(POS_FIELDS_ALT))) == 0


@pytest.mark.run(order=14)
def test_feature_eng_column_parado():
    poi, pos = get_poi_pos()
    pos = feature_eng(pos, poi, add_pois=True)
    assert (pos.parado == [False if i in [2,3] else True for i in range(10)]).all()


@pytest.mark.run(order=15)
def test_feature_eng_column_tempo_parado_e_andando():
    poi, pos = get_poi_pos()
    pos = feature_eng(pos, poi, add_pois=True)
    # If the state was changed from stoped to moving at k=2, keep moving at
    # k=3, and changed back to stoped at k=4, and considering 120 seconds
    # between measurements, the time spent in each bin will be:
    stoped = [0, 120, 60, 0, 60, 120, 120, 120, 120, 120]
    moving = [0, 0, 60, 120, 60, 0, 0, 0, 0, 0]

    assert (pos.tempo_parado == stoped).all()
    assert (pos.tempo_andando == moving).all()


@pytest.mark.run(order=16)
def test_feature_eng_find_pois():
    poi, pos = get_poi_pos()
    pos = feature_eng(pos, poi, add_pois=True)
    # POI 1 and 2 have the same radius: 350m. POI 2 center is approximately
    # 445m away from POI 1 center in latitude. The vehicle starts from POI 1
    # center and moves towards POI 2 center in and approximate rate of 90m
    # per measurement.
    # Therefore, the POIs would be:
    
    pois = ['PONTO 1', 'PONTO 1', 'PONTO 1,PONTO 2', 'PONTO 1,PONTO 2',
            'PONTO 2', 'PONTO 2', 'PONTO 2', 'PONTO 2', 'PONTO 2', 'Nenhum']
    
    assert (pos.POIs == pois).all()