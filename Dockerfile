FROM python:3.9-alpine

COPY . ./

ENV PORT 8080

RUN pip install Flask slack-sdk gunicorn openai

CMD gunicorn --bind :$PORT main:app