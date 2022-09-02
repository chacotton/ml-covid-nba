FROM python:3.8-slim-buster
WORKDIR data_ingestion
COPY . .
RUN pip install -r requirements.txt
CMD python db_test.py