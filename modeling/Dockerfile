FROM python:3.8-slim-buster
ENV date=2021-01-01
ENV season=2022
WORKDIR home
COPY . ./modeling
RUN pip install -r modeling/requirements.txt
CMD python -m modeling.main --win_model=classifier_v2 --covid_model=nbeats_50.pt --date=${date} -w -i -p --season=${season}