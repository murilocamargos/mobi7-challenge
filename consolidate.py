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


def get_time_in_poi(car, pos, poi):
    """
    Get a sequence with all POIs that contained a car with the amount of
    time spent in the POI.

    Parameters
    ----------
    car : str
        The vehicle identifier.

    pos : pd.DataFrame
        A data frame with the available position and state measurements
        from all vehicles.
    
    poi : pd.DataFrame
        A data frame with all positions of interest with name, radius and
        coordinates.
    
    Returns
    -------
    positions_with_time : list[POI, total time, stopped time]
        A sequence with local aggregations of the total time spent
        in a POI and the time stopped at that same POI.
    """
    # Use the fraction of the dataset related to the car
    pos_car = pos[pos.placa == car].reset_index().drop('index', axis=1)
    # List of all positions with time in sequence
    positions_with_time = []
    # Process each position measurement against the POIs
    curr_pos_with_time = [pos_car.POIs[0], 0, 0]
    for i in range(1, pos_car.shape[0]):
        if pos_car.POIs[i] == curr_pos_with_time[0]:
            # If the car didn't get out of the current POI, keep adding time
            curr_pos_with_time[1] += pos_car.tempo[i]
            if pos_car.parado[i]:
                curr_pos_with_time[2] += pos_car.tempo[i]
        
        else:
            # If the car got out of a POI or entered a different POI
            # split the time elapsed in the measurement between the previous
            # POI and the next one.
            curr_pos_with_time[1] += pos_car.tempo[i]/2
            if pos_car.parado[i]:
                curr_pos_with_time[2] += pos_car.tempo[i]/2
            
            positions_with_time.append(curr_pos_with_time)

            curr_pos_with_time = [pos_car.POIs[i], pos_car.tempo[i]/2, 0]
            if pos_car.parado[i]:
                curr_pos_with_time[2] += pos_car.tempo[i]/2
    
    # Add last car position to the list of POIs
    positions_with_time.append(curr_pos_with_time)

    return positions_with_time


def aggregate_positions_with_time(positions_with_time, car):
    """
    Parameters
    ----------
    positions_with_time : list
        A sequence with all POIs that contained a car with the amount of
        time spent in the POI.

    car : str
        The vehicle identifier.
    
    Returns
    -------
    df : pd.DataFrame
        A dataframe with the total and stopped time spent by a car in each
        POI.
    """
    # Sometimes the vehicles are in more than one POI simultaneously.
    # When this happens, the same amount of time will be recorded for
    # each POI.
    spl_pos_with_time = []
    for pwt in positions_with_time:
        spl_pos_with_time += [[i, pwt[1], pwt[2]] for i in pwt[0].split(',')]
    
    # Create the dataframe with the consolidated result
    df = pd.DataFrame(spl_pos_with_time, columns=['poi', 'total', 'parado']).\
        groupby('poi').sum().reset_index()
    df['placa'] = car

    return df


if __name__ == '__main__':
    pos, poi = get_data()
    pos = feature_eng(pos, add_pois=True)
    for car in pos.placa.unique():
        positions_with_time = get_time_in_poi(car, pos, poi)
        car_at_pois = aggregate_positions_with_time(positions_with_time, car)
        print(car_at_pois)
    print(pos)
