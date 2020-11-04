# Mobi7 Dash

## 1. Running Intructions
### 1.1. Set environment variables
1. Download the repo's content.
2. Rename `.flaskenv-example` to `.flaskenv`.
3. Copy your MapBox token in the `MAPBOX_TOKEN` line of `.flaskenv`.
4. Rename `.env-example` to `.env`.

### 1.2. Running the dashboard with/without airflow
#### 1.2.1. With airflow (running with Docker)
1. Run the docker-compose command: `docker-compose up`
2. Data can be consolidated through `airflow` admin at: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
3. Dashboard can be accessed at: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
4. The application can be tested using the following command:
```
docker exec -it mobi7-challenge_web_1 pytest -v
```
Please, note that the `mobi7-challenge_web_1` container name may change.

#### 1.2.2. Without airflow
1. Create a virtual environment with **python 3.8**: `python -m venv mobi7`
2. Activate your environment:
```
mobi7\Scripts\activate     # Windows
source mobi7/bin/activate  # Linux
```
3. Install the dependencies: `pip install -r requirements.txt`
4. Run the application: `python app.py`
5. This mode **does not** use airflow to consolidate data. You'll need to do it manually using: `python app.py --consolidate`
6. Dashboard can be accessed at: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
7. The application can be tested using the following command:
```
pytest --ignore=logs -v
```

## References
- Docs from: Python, Pytest, Flask, Docker, Bootstrap, jQuery, Apache Airflow.
- https://towardsdatascience.com/apache-airflow-and-postgresql-with-docker-and-docker-compose-5651766dfa96
- https://dzone.com/articles/running-apache-airflow-dag-with-docker
- https://blog.invivoo.com/creating-your-first-apache-airflow-dag/
- https://stackoverflow.com/questions/58762323/how-to-use-pythonvirtualenvoperator-in-airflow
- https://github.com/puckel/docker-airflow/issues/101