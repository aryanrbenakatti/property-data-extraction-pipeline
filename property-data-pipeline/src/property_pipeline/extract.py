"""HTML extraction helpers. The default demo uses a local fixture."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

SELECTORS = {
    "card": ".property-card",
    "title": ".title",
    "price": ".price",
    "location": ".location",
    "area": ".area",
    "property_type": ".property-type",
}

USER_AGENT = "PropertyDataPipeline/1.0 (portfolio demo; one request per run)"


def fetch_html(url: str, timeout: int = 15) -> str:
    """Fetch one public page. Call only when automated access is permitted."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must be a valid http or https URL.")
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response.text


def read_html_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _text(card: Any, selector: str) -> str | None:
    node = card.select_one(selector)
    if node is None:
        return None
    value = node.get_text(" ", strip=True)
    return value or None


def parse_listings(html: str, source: str, selectors: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Parse listing cards using configurable CSS selectors."""
    css = selectors or SELECTORS
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select(css["card"])
    records = []
    for card in cards:
        records.append({
            "title": _text(card, css["title"]),
            "price_raw": _text(card, css["price"]),
            "location_raw": _text(card, css["location"]),
            "area_raw": _text(card, css["area"]),
            "property_type": _text(card, css["property_type"]),
            "source": source,
        })
    return records
