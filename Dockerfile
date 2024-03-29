FROM python:3-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update
RUN apt install -y libpq-dev gcc

WORKDIR /magic_linker
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY manage.py .
COPY proj ./proj
COPY do.py .
COPY app ./app
COPY git-state.txt .
RUN ./do.py m -- collectstatic --no-input

EXPOSE 8004

ENTRYPOINT gunicorn\
	-w 1\
	-b 0.0.0.0:8004\
	proj.wsgi:application
