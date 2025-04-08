FROM ubuntu:jammy
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get upgrade -y && apt-get install -y g++

RUN uv python install 3.12

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
COPY main.py .

RUN uv sync --frozen

CMD ["uv", "run", "--no-sync", "fastapi", "run", "--host", "0.0.0.0", "--port", "8000", "/app/main.py"]
