"""Command-line entry point."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .extract import fetch_html, parse_listings, read_html_file
from .storage import save_outputs
from .transform import transform_records

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract, clean, and store property listing data.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--html", help="Path to a local HTML file (recommended demo mode).")
    source.add_argument("--url", help="One public URL you are permitted to access.")
    parser.add_argument("--out", default="output", help="Output directory (default: output).")
    args = parser.parse_args()

    if args.html:
        html = read_html_file(args.html)
        source_label = "local_fixture"
    else:
        logger.info("Fetching one URL. Ensure the site permits automated access.")
        html = fetch_html(args.url)
        source_label = args.url

    records = parse_listings(html, source_label)
    valid, invalid = transform_records(records)
    paths = save_outputs(valid, invalid, args.out)

    logger.info("Cards parsed: %d", len(records))
    logger.info("Valid unique records: %d", len(valid))
    logger.info("Invalid records for review: %d", len(invalid))
    for name, path in paths.items():
        logger.info("%s: %s", name, path)

    if valid.empty:
        logger.warning("No valid listings found. Check the page's HTML and CSS selectors.")


if __name__ == "__main__":
    main()
