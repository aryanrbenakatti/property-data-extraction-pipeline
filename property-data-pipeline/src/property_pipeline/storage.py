"""Exports cleaned data to CSV, JSON, and SQLite."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def save_outputs(valid: pd.DataFrame, invalid: pd.DataFrame, out_dir: str | Path) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / "properties.csv"
    json_path = out / "properties.json"
    db_path = out / "properties.db"
    invalid_path = out / "invalid_records.csv"

    valid.to_csv(csv_path, index=False)
    valid.to_json(json_path, orient="records", indent=2, force_ascii=False)
    invalid.to_csv(invalid_path, index=False)

    with sqlite3.connect(db_path) as connection:
        valid.to_sql("properties", connection, if_exists="replace", index=False)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city)
        """)
        connection.commit()

    return {
        "csv": str(csv_path),
        "json": str(json_path),
        "sqlite": str(db_path),
        "invalid": str(invalid_path),
    }
