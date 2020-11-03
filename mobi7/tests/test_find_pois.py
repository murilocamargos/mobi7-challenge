import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from mobi7.funcs import find_pois
from .helpers import get_valid_position, get_valid_poi


def test_find_pois():
    poi = get_valid_poi(2)
    poi.loc[1, 'latitude'] += 0.004
    poi.loc[1, 'nome'] = 'PONTO 2'
    
    position = get_valid_position()

    # Just on P1
    position.latitude = poi.latitude[0]
    position.longitude = poi.longitude[0]
    assert find_pois(position, poi) == 'PONTO 1'

    # Just on P2
    position.latitude = poi.latitude[1]
    position.longitude = poi.longitude[1]
    assert find_pois(position, poi) == 'PONTO 2'

    # In the intersection between P1 and P2
    position.latitude = (poi.latitude[0] + poi.latitude[1])/2
    position.longitude = (poi.longitude[0] + poi.longitude[1])/2
    assert find_pois(position, poi) == 'PONTO 1,PONTO 2'

    # Increase distance so there is no intersection
    poi.loc[1, 'latitude'] += 0.004
    position.latitude = (poi.latitude[0] + poi.latitude[1])/2
    position.longitude = (poi.longitude[0] + poi.longitude[1])/2
    assert find_pois(position, poi) == ''