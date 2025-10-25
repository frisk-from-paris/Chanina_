FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y \
    curl \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxcursor1 \
    libxfixes3 \
    libgtk-3-0 \
    libgbm1 \
    libcairo-gobject2 \
    libgdk-pixbuf-xlib-2.0-0 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m cha_worker

COPY pyproject.toml poetry.lock* ./
RUN pip install poetry 
COPY . /app/

USER cha_worker
ENV PYTHONPATH=/app/src
RUN poetry install --no-root
RUN poetry run playwright install

CMD ["poetry", "run", "celery", "-A", "tests.tests:celery", "worker", "--loglevel=info"]
