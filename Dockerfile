FROM ubuntu:jammy
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL org.opencontainers.image.source="https://github.com/nanth-uw/scispacy-dockerized"

RUN apt-get update && apt-get upgrade -y && apt-get install -y g++

RUN uv python install 3.12

ENV UVICORN_WORKERS=1

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
COPY main.py .

RUN uv sync --frozen --no-dev

CMD ["uv", "run", 
  "--no-sync", "fastapi", "run",
  "--host", "0.0.0.0",
  "--port", "8000",
  "--workers", $UVICORN_WORKERS,
  "/app/main.py"
]
