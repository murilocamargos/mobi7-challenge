import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from mobi7.funcs import find_pois
from .helpers import move_files_to_temp_folder


def test_find_pois_type_error():
    with pytest.raises(TypeError) as err:
        find_pois(1,2)
    assert str(err.value) == 'The `measurement` must be a pd.DataFrame.'
    
    with pytest.raises(TypeError) as err:
        find_pois(pd.DataFrame([{'teste': 1}]), 2)
    assert str(err.value) == 'The `list_of_pois` must be a pd.DataFrame.'