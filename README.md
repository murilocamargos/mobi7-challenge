# Mobi7 Dash

## Set environment variables
1. Rename `.flaskenv-example` to `.flaskenv`.
2. Copy your MapBox token in the `MAPBOX_TOKEN` line of `.flaskenv`.

## Run with Docker
1. Run the docker-compose command:
```docker-compose up``` 

## Run locally without Docker
1. Create a virtual environment with `python 3.8`: 
```python -m venv mobi7```
2. Activate your environment:
```mobi7\Scripts\activate```
3. Install the dependencies:
```pip install -r requirements.txt```
4. Run the application:
```python app.py```
5. If you need to consolidate the results, use:
```python app.py --consolidate```

## Open the dashboard
1. Access through your browser:
```http://127.0.0.1:5000/```


## References
- https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96
- https://dzone.com/articles/running-apache-airflow-dag-with-docker
- https://blog.invivoo.com/creating-your-first-apache-airflow-dag/