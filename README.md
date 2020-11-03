# Mobi7 Dash

## Running the dashboard
1. Rename `.flaskenv-example` to `.flaskenv`.

2. Copy your MapBox token in the `MAPBOX_TOKEN` line of `.flaskenv`.

3. Create a virtual environment with `python 3.8`: 
```python -m venv mobi7```

5. Activate your environment:
```mobi7\Scripts\activate```

5. Install the dependencies:
```pip install -r requirements.txt```

6. Run the application:
```python app.py```

7. Access through your browser:
```http://127.0.0.1:5000/```