FROM python:3.8-slim-buster
WORKDIR modeling
COPY . .
RUN pip install -r requirements.txt
CMD python main.py --model=/mnt/ml-nba/models/test_model