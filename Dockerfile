# syntax=docker/dockerfile:1
FROM python:3.9-alpine

WORKDIR /ip_app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./ip_app .

# change according to which port is used
EXPOSE 5000
             
# create the DB and serve with waitress
CMD ['flask', '--app ip_app', 'init-db']
CMD ['waitress-serve', '--call "ip_app:create_app"']
