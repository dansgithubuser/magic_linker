FROM python:3-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /magic_linker
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY manage.py .
COPY proj ./proj
COPY do.py .
COPY app ./app
COPY git-state.txt .
RUN ./do.py m -- collectstatic --no-input

EXPOSE 8000

ENTRYPOINT gunicorn\
	-w 4\
	-b 0.0.0.0:8000\
	proj.wsgi:application
