# Этап 1: Сборка зависимостей
FROM python:3.11-alpine AS builder
WORKDIR /app
COPY . /app
COPY ../.env /app
RUN pip install pipenv
RUN pipenv install --system
CMD ["python", "-m", "src.app"]