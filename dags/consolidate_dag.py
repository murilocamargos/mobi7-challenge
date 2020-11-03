from airflow import DAG
from airflow.operators.python_operator import PythonVirtualenvOperator
from airflow.utils.dates import days_ago
from datetime import timedelta


def consolidate_results():
    """Create a CSV file with the results consolidated.

    Returns
    -------
    res : pd.DataFrame
        A dataframe with the total and stopped time spent by each car in each
        POI.
    """
    import pandas as pd
    from pathlib import Path
    from geopy.distance import geodesic
    import sys

    sys.path.insert(0, '/opt/airflow/mobi7')
    from funcs import get_data, get_time_in_poi, aggregate_positions_with_time, feature_eng

    pos, poi, _ = get_data('/data')

    pos = feature_eng(pos, poi, add_pois=True, geodesic=geodesic)
    res = None
    for car in pos.placa.unique():
        positions_with_time = get_time_in_poi(car, pos, poi)
        car_at_pois = aggregate_positions_with_time(positions_with_time, car)
        
        if res is None:
            res = car_at_pois
        else:
            res = pd.concat((res, car_at_pois), axis=0).reset_index().\
                drop('index', axis=1)
    
    dir_path = Path('/data')
    res.to_csv(dir_path.joinpath('resultados_consolidado_POIs.csv'))

    return res


# initializing the default arguments that we'll pass to our DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(0),
    'email': ['murilo.camargosf@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

consolidate_dag = DAG(
    'consolidate_dag',
    default_args=default_args,
    description='Consolidate DAG',
    schedule_interval=timedelta(days=1),
)

task_1 = PythonVirtualenvOperator(
    task_id='consolidate_task',
    python_callable=consolidate_results,
    requirements=['geopy'],
    python_version='3',
    dag=consolidate_dag
)