FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /backend

COPY ./app ./app
COPY ./migrations ./migrations
COPY ./google-services.json ./
COPY ./pyproject.toml ./
COPY ./.python-version ./
COPY ./uv.lock ./

RUN uv pip compile pyproject.toml --output-file requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt
