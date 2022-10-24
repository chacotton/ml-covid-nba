FROM python:3.8-slim-buster
ENV date='2022-01-01'
WORKDIR home
COPY . ./data_ingestion
RUN apt-get update && apt-get install -y --no-install-recommends git
RUN pip install -r data_ingestion/requirements.txt
CMD python -m data_ingestion.main -p -t -r -d ${date}