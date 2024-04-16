# Stage 1: Build the Python app
FROM python:3.11-alpine AS build

WORKDIR /app

COPY Pipfile Pipfile.lock /app/
COPY .env /app/.env

RUN apk add --no-cache

COPY . /app

# Stage 2: Final image
FROM python:3.11-alpine

WORKDIR /app

COPY --from=build /app /app

RUN pip install pipenv && \
    pipenv install --system --deploy

CMD ["python", "main.py"]