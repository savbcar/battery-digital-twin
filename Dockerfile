FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY sql ./sql

RUN pip install --no-cache-dir .

ENTRYPOINT ["battery-twin"]
CMD ["all"]
