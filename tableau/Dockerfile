FROM python:3.8-slim-buster
WORKDIR tableau
COPY . .
RUN pip install -r requirements.txt
RUN pip install gunicorn
CMD gunicorn app:app