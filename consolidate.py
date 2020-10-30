import pandas as pd
from geopy.distance import geodesic


def get_data():
    """Get all data from the CSV files.

    Returns
    -------
    pos : pd.DataFrame
        A data frame with the available position and state measurements
        from all vehicles.

    poi : pd.DataFrame
        A data frame with all positions of interest with name, radius and
        coordinates.
    """
    pos = pd.read_csv('data/posicoes.csv')
    poi = pd.read_csv('data/base_pois_def.csv')
    return pos, poi


def find_pois(measurement, list_of_pois):
    """Find the POIs in the database that includes a given measurement.
    The distance function relies on a ellipsoidal model of the earth to
    find the shortest distance on the earth's surface.
    https://geopy.readthedocs.io/en/stable/#module-geopy.distance
    
    Parameters
    ----------
    measurement : pd.DataFrame
        An item of the pos data set containing latitude and longitude measures.

    poi : pd.DataFrame
        A data frame with all positions of interest with name, radius and
        coordinates.

    Returns
    -------
    pois : str
        A comma separated list of all POIs that contains the measurement.
    """
    pois = list_of_pois.apply(lambda poi: geodesic(
        (measurement.latitude, measurement.longitude),
        (poi.latitude, poi.longitude)).meters <= poi.raio, axis=1)
    pois = ','.join(poi[pois].nome)
    return pois


def feature_eng(pos, add_pois=False):
    """Add and transform features in the positions dataset to facilitate
    the analysis.

    Parameters
    ----------
    pos : pd.DataFrame
        A data frame with the available position and state measurements
        from all vehicles.
    
    add_pois : bool
        Adds the POIs feature or not. Finding the POIs for all measurements
        can have a big computational burden. Therefore, it is optional.
    
    Returns
    -------
    pos : pd.DataFrame
        The same dataframe with the modified features.
    """
    # Add column to identify stopped vehicles
    pos['parado'] = (pos.velocidade < 5) & (~pos.ignicao)

    # Convert all date strings to datetime
    pos.data_posicao = pos.data_posicao.apply(lambda x: pd.to_datetime(x[:-25]))

    # Compute the ellapsed time between measurements for each vehicle
    for placa in pos.placa.unique():
        pos.loc[pos['placa'] == placa] = pos.loc[pos['placa'] == placa].\
            sort_values(by='data_posicao')
        pos.loc[pos['placa'] == placa, 'tempo'] = pos[pos['placa'] == placa].\
            data_posicao.diff().apply(lambda x: x.seconds)

    # Compute stopped and moving times
    pos['tempo_parado'] = 0
    pos['tempo_andando'] = 0
    pos.loc[pos.parado, 'tempo_parado'] = pos[pos.parado].tempo
    pos.loc[~pos.parado, 'tempo_andando'] = pos[~pos.parado].tempo

    # Find POIs where the car has been
    if add_pois:
        pos['POIs'] = pos.apply(lambda x: find_pois(x, poi), axis=1)

    return pos


if __name__ == '__main__':
    pos, poi = get_data()
    pos = feature_eng(pos, add_pois=True)
    print(pos)
