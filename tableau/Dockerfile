FROM python:3.8-slim-buster
WORKDIR tableau
COPY . .
ADD ./images.tar.gz ./static
RUN pip install -r requirements.txt
RUN pip install gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]