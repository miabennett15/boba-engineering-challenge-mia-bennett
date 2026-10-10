# Boba Commodities Engineering Challenge

This project loads trade data from an Excel workbook into PostgreSQL, exposes the data through a FastAPI service, and supports filtering on trades and open positions.

## Requirements

- Python 3.11+
- PostgreSQL 16+
- A local or remote PostgreSQL instance
- Access to the Excel file at `data/trades.xlsx`

## Project structure

- `app/` — application code
  - `app/database.py` — SQLAlchemy base
  - `app/services/models.py` — trade table model
  - `app/main.py` — FastAPI endpoints
- `scripts/` — setup and import scripts
  - `scripts/setup_database.py` — create the PostgreSQL database if it does not already exist
  - `scripts/create_trade_tables.py` — clean, validate, and import workbook rows into the database
- `data/trades.xlsx` — source trade data
- `.env` — local runtime configuration

## 1. Clone the project

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy psycopg[binary] pandas python-dotenv openpyxl
```

If you prefer a requirements file, add these to `requirements.txt` and run:

```bash
pip install -r requirements.txt
```

## 4. Configure your environment

Copy the example environment file:

```bash
cp .env.example .env
```

Then update `.env` with your own PostgreSQL settings:

```env
DATABASE_NAME=trades_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

If you are using a remote database, change `DATABASE_HOST` and the credentials accordingly.

## 5. Create the PostgreSQL database

Run:

```bash
python scripts/setup_database.py
```

This checks whether the configured database exists and creates it if needed.

## 6. Import the trade data

Run:

```bash
python scripts/create_trade_tables.py
```

This script will:

- read the Excel workbook in `data/trades.xlsx`
- normalize column names
- validate required fields
- skip invalid or duplicate rows
- create the `trades` table if needed
- insert the valid trade records into PostgreSQL

## 7. Start the API

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

## API endpoints

### Get a single trade

```bash
curl http://127.0.0.1:8000/trades/10000
```

Returns a trade object with at least:

- `trade_id`
- `commodity`
- `contract`
- `size`
- `trader`
- `source_file`

### Search trades

```bash
curl "http://127.0.0.1:8000/trades?commodity=AB"
curl "http://127.0.0.1:8000/trades?contract=K2V2"
curl "http://127.0.0.1:8000/trades?trader=Trader+A"
```

You can combine filters:

```bash
curl "http://127.0.0.1:8000/trades?commodity=AB&trader=Trader+A"
```

### Get open positions

```bash
curl http://127.0.0.1:8000/positions
curl "http://127.0.0.1:8000/positions?commodity=AB"
```

Returns net quantity grouped by:

- `commodity`
- `contract`
- `net_quantity`

## Example response

### Trade response

```json
{
  "trade_id": 10000,
  "commodity": "AB",
  "contract": "K2V2",
  "size": -1160.0,
  "trader": "Trader A",
  "source_file": "trades.xlsx"
}
```

### Position response

```json
{
  "commodity": "AB",
  "contract": "F23",
  "net_quantity": -1670.0
}
```

## Notes

- The import script is intentionally defensive and skips incomplete or inconsistent rows rather than inserting broken data.
- The database name, credentials, and host are configured through `.env` so the project can run on local machines or remote environments.
- If you change the database host or credentials, update `.env` and rerun the setup/import scripts.

## Troubleshooting

### Module not found errors

Run the project from the repository root and ensure the virtual environment is active:

```bash
source .venv/bin/activate
```

### Database connection errors

Check that PostgreSQL is running and that the values in `.env` match your database setup.

### No rows imported

Confirm the workbook exists at `data/trades.xlsx` and that the expected columns are present.

## Summary

This project is designed to be run from a fresh checkout by:

1. creating a Python virtual environment,
2. installing required packages,
3. configuring `.env`,
4. creating the database,
5. importing the Excel records,
6. starting the FastAPI service on port 8000.
