import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from mobi7.funcs import feature_eng, get_time_in_poi, POS_FIELDS,\
                    aggregate_positions_with_time
from .helpers import get_valid_position, get_valid_poi, get_poi_pos


def test_get_time_in_poi_and_aggregation():
    poi, pos = get_poi_pos()
    pos = feature_eng(pos, poi, add_pois=True)
    # pois = ['PONTO 1', 'PONTO 1', 'PONTO 1,PONTO 2', 'PONTO 1,PONTO 2',
    #         'PONTO 2', 'PONTO 2', 'PONTO 2', 'PONTO 2', 'PONTO 2', 'Nenhum']
    # stoped = [0, 120, 60, 0, 60, 120, 120, 120, 120, 120]
    # moving = [0, 0, 60, 120, 60, 0, 0, 0, 0, 0]
    time_in_poi = [['PONTO 1', 180.0, 30.0], ['PONTO 1,PONTO 2', 240.0, 180.0],
                   ['PONTO 2', 600.0, 30.0], ['Nenhum', 60.0, 0.0]]
    
    aggregated_tip = [['PONTO 1', 420, 210], ['PONTO 2', 840, 210],
                      ['Nenhum', 60.0, 0.0]]
    
    gtip = get_time_in_poi(pos.loc[0, 'placa'], pos, poi)

    assert gtip == time_in_poi
    
    apwt = aggregate_positions_with_time(gtip, pos.loc[0, 'placa'])

    assert (apwt.columns == ['poi', 'total', 'parado', 'placa']).all()
    assert apwt[apwt.poi == 'PONTO 1'].total.values == aggregated_tip[0][1]
    assert apwt[apwt.poi == 'PONTO 1'].parado.values == aggregated_tip[0][2]
    assert apwt[apwt.poi == 'PONTO 2'].total.values == aggregated_tip[1][1]
    assert apwt[apwt.poi == 'PONTO 2'].parado.values == aggregated_tip[1][2]
    assert apwt[apwt.poi == 'Nenhum'].total.values == aggregated_tip[2][1]
    assert apwt[apwt.poi == 'Nenhum'].parado.values == aggregated_tip[2][2]
