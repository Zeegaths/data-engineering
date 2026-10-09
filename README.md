# data-engineering

Bitcoin mempool pipeline: pulls the latest blocks from the mempool.space API with Pandas, cleans them, and loads them into Postgres running in Docker.

## Files
- `ingest.py`: extract, clean, load with SQLAlchemy
- `Dockerfile`: builds the ingest script
- `docker-compose.yml`: `db` (Postgres) and `ingest` services

## Run
    docker compose up --build
    docker ps

## Query
    pgcli -h localhost -p 5432 -U postgres -d crypto
    SELECT * FROM btc_blocks LIMIT 5;
