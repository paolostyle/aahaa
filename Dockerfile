FROM python:3.8

RUN apt-get update -y
RUN apt-get -y install tesseract-ocr

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

RUN pip install gunicorn

COPY . /app

VOLUME /app/screens
VOLUME /app/debug

EXPOSE 8080
CMD ["gunicorn", "main:app", "-w", "4", "-b", "0.0.0.0:8080", "-k", "uvicorn.workers.UvicornWorker"]
