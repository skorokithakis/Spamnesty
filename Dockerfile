FROM python:latest
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y swig libssl-dev dpkg-dev netcat
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -Ur requirements.txt
