FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install pipenv
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN pipenv install

COPY . .
EXPOSE 8000

RUN ["chmod", "+x", "/app/entrypoint.sh"]
