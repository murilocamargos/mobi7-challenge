import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from ..funcs import feature_eng, POS_FIELDS
from .helpers import get_valid_position, get_valid_poi


def get_poi_pos_features():
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
    
    return feature_eng(position, poi, add_pois=True)


def test_feature_eng_columns():
    pos = get_poi_pos_features()
    POS_FIELDS_ALT = POS_FIELDS + ['parado', 'tempo_parado', 'tempo_andando',
        'POIs', 'tempo']
    assert len(set(pos.columns).difference(set(POS_FIELDS_ALT))) == 0


def test_feature_eng_column_parado():
    pos = get_poi_pos_features()
    assert (pos.parado == [False if i in [2,3] else True for i in range(10)]).all()


def test_feature_eng_column_tempo_parado_e_andando():
    pos = get_poi_pos_features()
    # If the state was changed from stoped to moving at k=2, keep moving at
    # k=3, and changed back to stoped at k=4, and considering 120 seconds
    # between measurements, the time spent in each bin will be:
    stoped = [0, 120, 60, 0, 60, 120, 120, 120, 120, 120]
    moving = [0, 0, 60, 120, 60, 0, 0, 0, 0, 0]

    assert (pos.tempo_parado == stoped).all()
    assert (pos.tempo_andando == moving).all()
