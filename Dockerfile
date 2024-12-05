FROM python:3.12-slim
ENV PYTHONUNBUFFERED 1
# Update and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      python3


RUN mkdir /app
WORKDIR /app

# Pip Env Setup
RUN pip install pipenv
COPY Pipfile* /app/

RUN pipenv install --deploy
RUN pipenv install --system

# Add the files to the app directory.
ADD . /app