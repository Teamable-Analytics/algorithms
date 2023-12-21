FROM python:3.9-slim-buster as builder

WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# lint
RUN python -m pip install --upgrade pip
COPY . /usr/src/app/

# install python dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
