"""Data cleaning, validation, and deduplication."""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any

import pandas as pd


def parse_numeric(value: Any) -> float | None:
    """Parse numeric text such as '1,250 sq ft' or '₹ 85,00,000'."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text:
        return None
    # Indian and international number formats are supported by removing separators.
    cleaned = re.sub(r"[^0-9.]", "", text.replace(",", ""))
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalise_city(location: Any) -> str | None:
    if location is None or (isinstance(location, float) and pd.isna(location)):
        return None
    text = re.sub(r"\s+", " ", str(location)).strip()
    if not text:
        return None
    # The demo uses "Area, City" or "City"; take the final comma-separated part.
    return text.split(",")[-1].strip().title()


def _listing_id(row: dict[str, Any]) -> str:
    parts = [
        str(row.get("title") or "").strip().lower(),
        str(row.get("price_inr") or ""),
        str(row.get("city") or "").strip().lower(),
        str(row.get("area_sqft") or ""),
        str(row.get("property_type") or "").strip().lower(),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def transform_records(records: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (valid, invalid) DataFrames. Invalid records are retained for review."""
    if not records:
        columns = ["listing_id", "title", "price_inr", "city", "area_sqft",
                   "property_type", "source", "scraped_at_utc"]
        return pd.DataFrame(columns=columns), pd.DataFrame(columns=["title", "reason"])

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    valid_rows: list[dict[str, Any]] = []
    invalid_rows: list[dict[str, Any]] = []

    for record in records:
        title = (record.get("title") or "").strip()
        price = parse_numeric(record.get("price_raw"))
        area = parse_numeric(record.get("area_raw"))
        city = normalise_city(record.get("location_raw"))
        property_type = (record.get("property_type") or "").strip() or None
        issues = []
        if not title:
            issues.append("missing title")
        if not city:
            issues.append("missing location/city")
        if issues:
            invalid_rows.append({**record, "reason": "; ".join(issues)})
            continue

        row = {
            "title": title,
            "price_inr": int(price) if price is not None else None,
            "city": city,
            "area_sqft": int(area) if area is not None else None,
            "property_type": property_type,
            "source": record.get("source") or "unknown",
            "scraped_at_utc": now,
        }
        row["listing_id"] = _listing_id(row)
        valid_rows.append(row)

    columns = ["listing_id", "title", "price_inr", "city", "area_sqft",
               "property_type", "source", "scraped_at_utc"]
    valid = pd.DataFrame(valid_rows, columns=columns)
    invalid = pd.DataFrame(invalid_rows)
    if not valid.empty:
        valid = valid.drop_duplicates(subset=["listing_id"], keep="first").reset_index(drop=True)
    return valid, invalid
