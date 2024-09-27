FROM python:3.9-slim-buster as builder

WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m pip install --upgrade pip
COPY . /usr/src/app/

RUN apt-get update
RUN apt-get -y install gcc libpq-dev python3-dev

# install python dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
