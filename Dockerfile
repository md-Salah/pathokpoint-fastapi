FROM python:3.11.8-slim-bullseye
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "run.py"]
