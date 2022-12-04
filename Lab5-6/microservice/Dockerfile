FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /microservice

RUN pip install pipenv
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN pipenv install

COPY . .
EXPOSE 8001

RUN chmod +x /microservice/entrypoint.sh
