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
    import sys
    sys.path.insert(0, '/opt/airflow/mobi7')
    from funcs import consolidate_results
    consolidate_results(dir_path='/data')


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