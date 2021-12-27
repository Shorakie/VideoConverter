FROM python:3.9-slim
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

RUN mkdir /api
WORKDIR /api

COPY requirements.txt /api/
RUN pip3 install -r requirements.txt

COPY . /api/

RUN ["chmod", "+x", "/api/docker/docker-entrypoint.sh"]
ENTRYPOINT ["/api/docker/docker-entrypoint.sh"]

EXPOSE 8000

CMD python /api/manage.py runserver 0.0.0.0:8000
