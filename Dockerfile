FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y swig libssl-dev dpkg-dev netcat gfortran libopenblas-dev liblapack-dev

# Fetch smtp2http from IPFS so we can run it in Docker.
RUN wget -O /usr/local/bin/smtp2http https://ipfs.eternum.io/ipfs/QmP3WsHbScbpzuGLK2PNF6r51ZgJuTbPbv51us6rbs94Ax/smtp2http

RUN pip install -U pip poetry
ADD poetry.lock /code/
ADD pyproject.toml /code/
RUN poetry config virtualenvs.create false
WORKDIR /code
RUN poetry install --no-dev --no-interaction

ADD misc/dokku/CHECKS /app/
ADD misc/dokku/* /code/

COPY . /code/
RUN /code/manage.py collectstatic --noinput
