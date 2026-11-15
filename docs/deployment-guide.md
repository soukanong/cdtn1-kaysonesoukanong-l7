# Deployment Guide – L7 Customer Data Quality (track DA)

Written for someone who does not know the system. Two services: `db` (PostgreSQL 16) and `app` (the pipeline code and the Streamlit dashboard on port 8501). No Python or PostgreSQL is needed on the computer.

## 1. Requirements

| Item | Value |
|---|---|
| Operating system | Windows 10/11, macOS or Linux (64-bit); tested on Windows |
| Docker | Docker Desktop with Compose v2. Tested with Docker Desktop 4.97.0 (Engine 29.9.2); Compose v2.x |
| Git | git version 2.40+ (Windows) |
| Disk and memory | about 2 GB free disk for images; 4 GB RAM available to Docker |
| Free ports | 8501 (dashboard) and 5433 (PostgreSQL, published port). To change a port, edit the left number in the `ports:` lines of `docker-compose.yml` |
| Network | Internet access for the first build (Docker images and pip packages) |

## 2. Setup steps

Run each command in a terminal (Windows: PowerShell), in this order.

```bash
git clone --branch v1.0 https://github.com/soukanong/cdtn1-kaysonesoukanong-l7.git
cd cdtn1-kaysonesoukanong-l7
cp .env.example .env            # PowerShell: Copy-Item .env.example .env
docker compose up -d --build    # the first build takes about 3-4 minutes
```

The `app` service first runs the pipeline (`python -m src.pipeline`), which creates the schema (the `sql/*.sql` scripts are idempotent) and loads the bundled sample `data/mau/customers_raw_sample.csv` because the real file is not in the image; it then starts the dashboard. Open <http://localhost:8501> when both services are `healthy`.

Stop (data kept): `docker compose down`. Start again from an empty database: `docker compose down -v`, then the last command.

## 3. Environment variables

All variables are in `.env` (created in step 2 from `.env.example`). `.env` is never committed.

| Name | Meaning | Sample value | Required |
|---|---|---|---|
| `POSTGRES_USER` | Database account created by the `db` container | `l7_user` | yes |
| `POSTGRES_PASSWORD` | Database password (sample value only; change it outside a demo) | `change_me` | yes |
| `POSTGRES_DB` | Database name | `l7_dq` | yes |
| `DWH_URL` | SQLAlchemy connection string used by the pipeline and dashboard. Inside Docker Compose it is overridden to host `db`, port 5432. When running Python on the host, use port 5433 (the published port) | `postgresql+psycopg://l7_user:change_me@localhost:5432/l7_dq` (as in `.env.example`) | yes when running outside Docker |
| `SOURCE_CSV` | Source file. Empty: use `data/customers_raw.csv` if it exists, otherwise `data/mau/customers_raw_sample.csv` | empty | no |
| `THRESHOLDS_FILE` | File with the quality thresholds | `configs/thresholds.yaml` | no |
| `REPORT_DIR` | Folder where quality reports are written | `reports` | no |
| `LOG_LEVEL` | Log level | `INFO` | no |

## 4. Sample data

The real file `customers_raw.csv` (67,037 rows) contains customer records and is not in the repository or in the Docker image, so `data/mau/customers_raw_sample.csv` (400 rows) is loaded automatically at start-up. Expected result:

| What | Count |
|---|---|
| Rows read | 400 |
| Rejected: `PHONE_MISSING` / `PHONE_INVALID` / `NAME_MISSING` | 49 (26 / 17 / 6) |
| Clean customers (`core.customer_clean`) | 323 |
| Records attached to an earlier record with the same phone (QT-01) | 28 |
| Records in suspected-duplicate groups (`core.duplicate_review`) | 47 (23 groups) |
| Rows in `dwh.fact_dq_issue` | 468 |
| Clean score (CLEAN stage) | 97.58 |

The rows add up: 400 read = 323 clean + 28 attached + 49 rejected (400 − 49 = 351, and 351 − 323 = 28 records share a phone with an earlier one).

Check one count:

```bash
docker compose exec db psql -U l7_user -d l7_dq -c "select count(*) from core.customer_clean;"   # expected: 323
```

Running the pipeline again (`docker compose run --rm app python -m src.pipeline`) does not change these counts.

## 5. Verify it works

| # | Command or action | Expected result |
|---|---|---|
| 1 | `docker compose ps` | `db` and `app` show `Up … (healthy)` (`app` can take 1–2 minutes after the build) |
| 2 | `curl -s http://localhost:8501/_stcore/health` (PowerShell: `curl.exe`) | `ok` |
| 3 | `docker compose logs app --tail 20` | a line `Kết luận: THANH_CONG (mã thoát 0)` |
| 4 | `docker compose run --rm --no-deps app python -m pytest -q` | `45 passed` |
| 5 | `docker compose run --rm app python -m src.pipeline` (second run), then count rows as above | exit code 0; the counts of section 4 do not change |
| 6 | Open <http://localhost:8501> | three tabs; tab 1 shows the RAW vs CLEAN chart with clean score 97.58 on the sample |
| 7 | `docker compose stop db`, then reload the page | a short error message with the error type only, no connection string, and a retry button. Restart with `docker compose start db` |

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `failed to connect to the docker API ... dockerDesktopLinuxEngine` | Docker Desktop is not running | start Docker Desktop and wait until the engine runs; check with `docker version` (both Client and Server must appear) |
| `port is already allocated` | another program uses 8501 or 5433 | stop that program, or change the left port number in `docker-compose.yml` |
| `app` is not healthy or restarts | cannot reach the database or the data file | `docker compose logs app` |
| the pipeline exits with code 2 | quality gate failed (DQ01–DQ04 below threshold on the clean data) | read the quality report printed in the log |
| the build fails while installing packages | a package in `requirements.txt` is not available on Linux | remove or replace that package, keep every line pinned with `==` |
