# BhavCopy

### Introduction:

This application is created as an exercise to download BSE bhavcopy from its site to parse and save into the Redis.
There is a Celery worker that run on every day at 18:00 IST to check for the latest version of bhavcopy. If found,
override the new data in redis.

After that Render a simple VueJs frontend with a search box that allows the stored entries to be searched by name and
renders a table of result. And there is an option to download CSV

### Technology Stack:

- Python 3.6
- Django 3.2
- Celery 5.0
- Redis
- VueJS
- Bootstrap 5 for css
- Icons8 for icons

### Setup

##### Prerequisites:

- Python 3.6 should be installed on your machine
- Create virtual environment of python 3.6
- Install package from ```requirements.txt```
- Create the ```.env``` file in project root to load environment data from the ```.env.template```

##### To run on a local machine:

- python manage.py runserver 0.0.0.0:8000
- celery -A bhavcopy worker -l INFO
- celery -A bhavcopy beat -l INFO
