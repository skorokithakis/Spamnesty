FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y swig libssl-dev dpkg-dev netcat

RUN pip install -U pip pipenv
ADD Pipfile* /code/
WORKDIR /code
RUN pipenv install --system

ADD misc/dokku/CHECKS /app/
ADD misc/dokku/* /code/

WORKDIR /code

COPY . /code/
RUN /code/manage.py collectstatic --noinput
