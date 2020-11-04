import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from ..funcs import feature_eng, get_time_in_poi, POS_FIELDS
from .helpers import get_valid_position, get_valid_poi, get_poi_pos


@pytest.mark.run(order=17)
def test_get_time_in_poi():
    poi, pos = get_poi_pos()
    pos = feature_eng(pos, poi, add_pois=True)
    POS_FIELDS_ALT = POS_FIELDS + ['parado', 'tempo_parado', 'tempo_andando',
        'POIs', 'tempo']
    assert len(set(pos.columns).difference(set(POS_FIELDS_ALT))) == 0