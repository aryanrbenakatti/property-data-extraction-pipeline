# Property Data Extraction & Cleaning Pipeline

A portfolio project demonstrating a small, reproducible data pipeline for property-style listing data. It extracts records from HTML using **Requests + BeautifulSoup**, cleans and validates them with **Pandas**, exports CSV/JSON, and loads records into **SQLite** for analysis.

> **Data and responsible use:** The included demo runs on a local HTML fixture, so it works without internet access and does not misrepresent sample data as live listings. The optional URL mode is intended only for pages you are permitted to access. Check a site's terms and `robots.txt`, use a reasonable request rate, and do not bypass logins, paywalls, CAPTCHAs, or access controls.

## Features

- Parse listing cards from HTML using configurable CSS selectors.
- Normalise prices, area, location, and property type.
- Validate required fields and report invalid records.
- Deduplicate records using a stable key.
- Export cleaned records to CSV and JSON.
- Load results into SQLite and run SQL summary queries.
- Logging, error handling, unit tests, and a local fixture for reproducible runs.

## Project structure

```text
property-data-pipeline/
├── data/
│   └── sample_listings.html
├── output/                 # generated on run; gitignored
├── src/
│   └── property_pipeline/
│       ├── __init__.py
│       ├── cli.py
│       ├── extract.py
│       ├── transform.py
│       └── storage.py
├── tests/
│   └── test_pipeline.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

Python 3.10+ is recommended.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the local demo

```bash
python -m src.property_pipeline.cli --html data/sample_listings.html --out output
```

The pipeline writes:
- `output/properties.csv`
- `output/properties.json`
- `output/properties.db`
- `output/invalid_records.csv`

Then inspect the SQLite database:

```bash
python -c "import sqlite3; c=sqlite3.connect('output/properties.db'); print(c.execute('SELECT city, COUNT(*), ROUND(AVG(price_inr)) FROM properties GROUP BY city').fetchall())"
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Optional URL extraction

Only use a public page when you have permission and the site's terms allow automated access. The parser expects listing cards with these CSS selectors:

- card: `.property-card`
- title: `.title`
- price: `.price`
- location: `.location`
- area: `.area`
- property type: `.property-type`

Example:

```bash
python -m src.property_pipeline.cli --url "https://example.org/permitted-listings-page" --out output
```

The page must use compatible HTML selectors. Update `SELECTORS` in `src/property_pipeline/extract.py` for a permitted source's structure. The tool makes one request only; it does not crawl links or paginate.

## Data schema

| Field | Description |
|---|---|
| `listing_id` | Stable hash derived from normalised listing attributes |
| `title` | Listing title |
| `price_inr` | Parsed numeric price in INR, when present |
| `city` | Location/city text |
| `area_sqft` | Numeric area in square feet, when present |
| `property_type` | Listing/property type |
| `source` | `local_fixture` or source URL |
| `scraped_at_utc` | UTC timestamp of extraction |

## Design choices and insights

1. **Separate extraction from transformation.** HTML parsing and data cleaning are separate modules, so each can be tested independently.
2. **Keep invalid rows visible.** Records missing essential information are written to `invalid_records.csv` rather than silently discarded.
3. **Make the demo reproducible.** The local fixture ensures recruiters can run and test the project without relying on a live website.
4. **Use SQLite for a lightweight data store.** It demonstrates loading and querying structured data without requiring a separate database server.

## Limitations and possible improvements

- Source-specific selectors need adjustment for each permitted website.
- This version does not crawl multiple pages, schedule jobs, or monitor listing changes.
- Price parsing is designed for common INR formats and should be adapted for other currencies.
- Next steps: add a source adapter interface, pytest coverage, Docker, scheduled runs, and a dashboard.

## Interview walkthrough

Be ready to explain the request/parse/clean/validate/deduplicate/export flow, how the ID is generated, how missing values are handled, and how you would make the pipeline reliable for a larger dataset.
