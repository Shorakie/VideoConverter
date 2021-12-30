# MyDong Backend Server
REST API server hosting `Video Converter` service.
The Project is written in `Python` and is based on `Django` and `Django Rest Framework`


# Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

The project is Dockerized

## Prerequisites

- Python 3.7+
- Django
- Django Rest Framework
- Docker


## Installing

After cloning the project we setup a virtual environment and install dependencies

```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ python install -r requirements.txt
```

Build a docker image

```
$ docker-compose -f docker/docker-compose.yml -p video_converter build
```

Migrate the changes using the web container.

```
$ docker-compose -f docker/docker-compose.yml -p video_converter run web --migrate
```

Create a Django superuser, make sure to replace the `EMAIL` and `USERNAME`.

```
$ docker-compose -f docker/docker-compose.yml -p video_converter run web python manage.py createsuperuser --email EMAIL --username USERNAME
```

## Running the Server

```
$ docker-compose -f docker/docker-compose.yml -p video_converter up -d
```


# Project structure                                                     

```
[project_name]
├── docker
│   ├── docker-compose.yml
│   ├── docker-entrypoint.sh
│   └── Dockerfile
├── apps
│   ├── authentication
│   │   ├── migrations
│   │   ├── apps.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   └── video
│       ├── migrations
│       ├── apps.py
│       ├── models.py
│       ├── serializers.py
│       ├── tasks.py
│       ├── urls.py
│       └── views.py
├── config
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core
│   ├── middlewares.py
│   ├── utils.py
│   └── validators.py
├── media
│   ├── converted
│   └── source
├── manage.py
├── nginx.conf
├── README.md
├── requirements.txt
└── supervisord.conf
```

The `docker/` directory is where are the configuration files needed to run the application with docker.

The `config/` contains The configuration root of the project, where project-wide settings, `urls.py`, `celery.py`, and `wsgi.py` modules are placed.

The `core/` contains The common problem solutions like `middlewares.py`, `permissions.py`, etc.

The `media/source` contains all the uploaded videos sent by users which are in queue to be converted or are converting

The `media/converted` contains all the converted videos which can be downloaded by the user

The `apps/` contains Django applications which are `authentication` and `video`

| App               | Purpose       |
| ----------------- | ------------- |
| `authentication`  | Used for user registration, authentication and refreshing JWT tokens|
| `video`           | Manages user submitted videos for conversion. used to upload a video or query a list or a specific video|


# Built With

- [Django](https://www.djangoproject.com) - The web framework
- [Django Rest Framework](https://www.django-rest-framework.org) - The REST frame work
- [Celery](https://docs.celeryproject.org) - Task Queue
- [RabbitMQ](https://www.rabbitmq.com) - Message Broker
- [PostgresSQL](https://www.postgresql.org) - Database
- [NginX](https://www.nginx.com) - Serve converted files
- [django-yasg](https://drf-yasg.readthedocs.io) - Auto generate swagger documentation

# Authors

- **Mohamad Amin Jafari** - *Initial work* - [Shorakie](https://github.com/Shorakie)


# License

This project is licensed under the `TBD` License - see the [LICENSE.md](LICENSE.md) file for details.
