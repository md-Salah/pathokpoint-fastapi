FROM python:3.11.8-slim
COPY . /app
WORKDIR /app
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2 \
    && pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "run.py"]
