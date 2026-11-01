"""
Test to ensure docs/CLAIMS.md matches what scripts/make_claims.py generates.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scripts.make_claims import generate_claims_table


def test_claims_md_matches_generator():
    claims_path = os.path.join(ROOT, "docs", "CLAIMS.md")
    assert os.path.exists(claims_path), "docs/CLAIMS.md does not exist"

    with open(claims_path, "r", encoding="utf-8") as f:
        existing_content = f.read()

    expected_content = generate_claims_table()
    assert existing_content.strip() == expected_content.strip(), (
        "docs/CLAIMS.md differs from scripts/make_claims.py output. "
        "Run `python scripts/make_claims.py` to regenerate."
    )
