# Fetching official base image for python
FROM python:3.9-slim-buster  as algorithms

# Setting up the work directory
WORKDIR /home/app/

# Preventing python from writing
# pyc to docker container
ENV PYTHONDONTWRITEBYTECODE 1

# Flushing out python buffer
ENV PYTHONUNBUFFERED 1

# Upgrading pip version
RUN python3 -m pip install --upgrade pip

# Copying requirement file
COPY requirements.txt .

## Installing dependencies
RUN python3 -m pip install gunicorn

# Installing dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copying all the files in our project
COPY . .
