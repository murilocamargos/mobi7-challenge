from flask import url_for

from mobi7.funcs import feature_eng, get_results
from mobi7.utils import zoom_center
from .helpers import get_poi_pos



def mock_get_dash_data():
    poi, pos = get_poi_pos()
    res = get_results(pos, poi)
    return pos, poi, res


def test_dash_api_get_path_without_plate(client):
    cli = client.get(url_for('dash.api_get_path'))
    assert cli.status_code == 404
    assert cli.json == {'error': 'Car not found.'}

    cli = client.get(url_for('dash.api_get_path', placa='TESTE002'))
    assert cli.status_code == 404
    assert cli.json == {'error': 'Car not found.'}


def test_dash_api_get_path_with_plate(mocker, client):
    mocker.patch("mobi7.routes.get_dash_data", return_value=mock_get_dash_data())
    cli = client.get(url_for('dash.api_get_path', placa='TESTE001'))
    assert cli.status_code == 200

    latlon = [[-25.56742701740896, -51.47653363645077]]
    for i in range(1,10):
        latlon.append([latlon[i-1][0] + 0.0008, latlon[i-1][1]])
    zoom, center = zoom_center([i[1] for i in latlon], [i[0] for i in latlon])

    assert cli.json['latlon'] == latlon
    assert cli.json['center'] == center
    assert cli.json['zoom'] == zoom
