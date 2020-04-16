FROM python:3.8

RUN pip install pipenv gunicorn uvloop

COPY . ./app
VOLUME /app/screens

WORKDIR /app

RUN pipenv install --system

EXPOSE 8080

CMD ["gunicorn", "main:app", "-w", "4", "-b", "0.0.0.0:8080", "-k", "uvicorn.workers.UvicornWorker"]
