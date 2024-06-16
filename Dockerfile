FROM python:3.10-alpine3.20
LABEL authors="whyAreWeFiveTeam"

ENV PYTHONUNBUFFERED 1

WORKDIR /library_app

ENV PYTHONPATH=${PYTHONPATH}:/library_app/management/commands

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .