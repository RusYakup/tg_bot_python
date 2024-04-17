# Этап 1: Сборка зависимостей
FROM python:3.11-alpine AS builder
WORKDIR /app
COPY . /app
RUN pip install pipenv

# Этап 2: Запуск приложения
FROM python:3.11-alpine
RUN pip install pipenv
WORKDIR /app
COPY --from=builder /app /app
RUN pipenv install --system --deploy
CMD ["python", "main.py"]