FROM python:latest
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y swig libssl-dev dpkg-dev netcat
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip install -U pip
RUN pip install -Ur requirements.txt
RUN /code/manage.py collectstatic --noinput
RUN git rev-parse --short HEAD > /code/git-rev.txt
RUN rm -rf /code/.git
CMD ["/code/misc/tooling/prod_run.sh"]
