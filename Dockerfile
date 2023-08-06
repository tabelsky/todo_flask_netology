FROM python:3.10.13-alpine3.18
COPY ./app /app

WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt

ENTRYPOINT gunicorn main:app --bind 0.0.0.0:5000
