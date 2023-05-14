# syntax=docker/dockerfile:1
FROM python:3.9-alpine

WORKDIR /ip_app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ['waitress-serve', '--call "ip_app:create_app"']
