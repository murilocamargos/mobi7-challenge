FROM python:3.8.6

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install -r ./requirements.txt

COPY . /app/

# ENTRYPOINT /bin/bash
EXPOSE 5000

ENTRYPOINT python ./app.py