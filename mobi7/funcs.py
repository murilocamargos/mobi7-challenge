from pathlib import Path
import pandas as pd
import numpy as np


POS_FIELDS = ['placa', 'data_posicao', 'velocidade', 'longitude', 'latitude',
              'ignicao']
POI_FIELDS = ['nome', 'raio', 'latitude', 'longitude']
RES_FIELDS = ['Unnamed: 0', 'poi', 'total', 'parado', 'placa']


def check_numeric(data, var_name, vmin=-np.inf, vmax=np.inf, check_as='df'):
    isnum = lambda x: np.issubdtype(x, np.number)

    if (check_as == 'sr' and not isnum(type(data))) or \
        (check_as == 'df' and not isnum(data.dtype)):
        raise TypeError(f'The `{var_name}` field must be numeric.')

    check_intv = (data <= vmax) & (data >= vmin)
    if (check_as == 'sr' and not check_intv) or \
        (check_as == 'df' and not check_intv.all()):
        raise ValueError(f'All `{var_name}` values must be in [{vmin},{vmax}].')


def check_data(data, var_name, fields, check_as='df'):
    """Check data from positions and POIs.

    Parameters
    ----------
    data : Series or DataFrame
        The data to be analyzed. It can be either a Series or a
        full DataFrame.
    
    var_name : str
        The name of the variables being checked.
    
    fields : list[str]
        The list of required fields that will be checked.
    
    check_as : str
        How the data will be checked, as a Series or as a DataFrame.
    """
    types = {'sr': pd.core.series.Series, 'df': pd.core.frame.DataFrame}
    if check_as not in types:
        raise ValueError('Please, choose a valid type.')

    if type(data) != types[check_as]:
        raise TypeError(f'The variable `{var_name}` must be a '\
                        f'{types[check_as].__name__}.')
    
    data_fields = data.index
    data_shape = data.shape[0]
    if check_as == 'df':
        data_fields = data.columns
        data_shape = data.shape[1]

    if data_shape != len(fields) or (data_shape != len(fields) and\
        not (sorted(data_fields) == sorted(fields)).all()):
        raise ValueError(f'The `{var_name}` {types[check_as].__name__} '\
                         f'should have the following fields: {fields}')
    
    if 'latitude' in data_fields:
        check_numeric(data.latitude, 'latitude', -90, 90, check_as)
    
    if 'longitude' in data_fields:
        check_numeric(data.longitude, 'longitude', -180, 180, check_as)
    
    if 'raio' in data_fields:
        check_numeric(data.raio, 'raio', 0, check_as=check_as)


def get_data(dir_path='./data'):
    """Get all data from the CSV files.

    Parameters
    ----------
    path : str
        The data path

    Returns
    -------
    pos : pd.DataFrame
        A data frame with the available position and state measurements
        from all vehicles.

    poi : pd.DataFrame
        A data frame with all positions of interest with name, radius and
        coordinates.
    
    cons : pd.DataFrame or None
        A data frame with the analysis result (if the file exists).
    """
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        raise NotADirectoryError('The `dir` must be a directory.')

    pos_file = dir_path.joinpath('posicoes.csv')
    poi_file = dir_path.joinpath('base_pois_def.csv')
    res_file = dir_path.joinpath('resultados_consolidado_POIs.csv')

    if not pos_file.exists():
        full = str(pos_file.absolute())
        raise FileNotFoundError(f'The positions file `{full}` was not found.')
    
    if not poi_file.exists():
        full = str(poi_file.absolute())
        raise FileNotFoundError(f'The POIs file `{full}` was not found.')

    pos = pd.read_csv(pos_file)
    poi = pd.read_csv(poi_file)

    cons = None
    if res_file.exists():
        cons = pd.read_csv(res_file)

    return pos, poi, cons


def find_pois(measurement, list_of_pois):
    """Find the POIs in the database that includes a given measurement.
    The distance function relies on a ellipsoidal model of the earth to
    find the shortest distance on the earth's surface.
    https://geopy.readthedocs.io/en/stable/#module-geopy.distance
    
    Parameters
    ----------
    measurement : pd.Series
        An item of the pos data set containing latitude and longitude measures.

    poi : pd.DataFrame
        A data frame with all positions of interest with name, radius and
        coordinates.

    Returns
    -------
    pois : str
        A comma separated list of all POIs that contains the measurement.
    """
    check_data(measurement, 'measurement', POS_FIELDS, 'sr')
    check_data(list_of_pois, 'list_of_pois', POI_FIELDS, 'df')
    
    from geopy.distance import geodesic
    
    pois = list_of_pois.apply(lambda poi: geodesic(
        (measurement.latitude, measurement.longitude),
        (poi.latitude, poi.longitude)).meters <= poi.raio, axis=1)
    pois = ','.join(list_of_pois[pois].nome)
    return pois


def feature_eng(pos, poi, add_pois=False):
    """Add and transform features in the positions dataset to facilitate
    the analysis.

    Parameters
    ----------
    pos : pd.DataFrame
        A data frame with the available position and state measurements
        from all vehicles.
    
    poi : pd.DataFrame
        A data frame with all positions of interest with name, radius and
        coordinates.
    
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
        pos.loc[pos['POIs'] == '', 'POIs'] = 'Nenhum'

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


def consolidate_results(dir_path='./data', provided_poi=None, save_file=True):
    """Create a CSV file with the results consolidated.

    Parameters
    ----------
    path : str
        The data path

    provided_poi : pd.DataFrame or None
        A data frame with the position of interest with radius and
        coordinates. This will override the POIs CSV file.

    save_file : bool
        Switch that allows saving or not the results file.
    
    Returns
    -------
    res : pd.DataFrame
        A dataframe with the total and stopped time spent by each car in each
        POI.
    """
    pos, poi, _ = get_data(dir_path)
    if provided_poi is not None:
        poi = provided_poi

    pos = feature_eng(pos, poi, add_pois=True)
    res = None
    for car in pos.placa.unique():
        positions_with_time = get_time_in_poi(car, pos, poi)
        car_at_pois = aggregate_positions_with_time(positions_with_time, car)
        
        if res is None:
            res = car_at_pois
        else:
            res = pd.concat((res, car_at_pois), axis=0).reset_index().\
                drop('index', axis=1)
    
    if save_file:
        dir_path = Path(dir_path)
        res.to_csv(dir_path.joinpath('resultados_consolidado_POIs.csv'))

    return res
