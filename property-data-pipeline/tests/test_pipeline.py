import unittest
from pathlib import Path

from src.property_pipeline.extract import parse_listings, read_html_file
from src.property_pipeline.transform import normalise_city, parse_numeric, transform_records

ROOT = Path(__file__).resolve().parents[1]


class TransformTests(unittest.TestCase):
    def test_parse_numeric_indian_price(self):
        self.assertEqual(parse_numeric("₹ 85,00,000"), 8500000)

    def test_parse_numeric_area(self):
        self.assertEqual(parse_numeric("1,250 sq ft"), 1250)

    def test_normalise_city(self):
        self.assertEqual(normalise_city("Green Park, Bengaluru"), "Bengaluru")

    def test_pipeline_deduplicates_and_keeps_invalid(self):
        html = read_html_file(ROOT / "data" / "sample_listings.html")
        records = parse_listings(html, "local_fixture")
        valid, invalid = transform_records(records)
        self.assertEqual(len(records), 5)
        self.assertEqual(len(valid), 3)  # duplicate removed
        self.assertEqual(len(invalid), 1)  # missing location
        self.assertIn("listing_id", valid.columns)
        self.assertEqual(set(valid["city"]), {"Bengaluru", "Pune"})


if __name__ == "__main__":
    unittest.main()
