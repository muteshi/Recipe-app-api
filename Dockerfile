FROM python:3.7-alpine
LABEL maintainer="Muteshi dev@webgurus.co.ke"

ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY ./app/ /app

#create user and switch to the user
RUN adduser -D user
USER user