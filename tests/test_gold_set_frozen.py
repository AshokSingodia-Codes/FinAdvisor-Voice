import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_gold_set_test_hash_unchanged():
    test_path = os.path.join(ROOT, "tests", "eval", "gold_set_test.json")
    hash_path = os.path.join(ROOT, "tests", "eval", "gold_set_test.sha256")

    assert os.path.exists(test_path), "gold_set_test.json missing"
    assert os.path.exists(hash_path), "gold_set_test.sha256 missing"

    with open(test_path, "rb") as f:
        actual_sha256 = hashlib.sha256(f.read()).hexdigest()

    with open(hash_path, "r", encoding="utf-8") as f:
        expected_sha256 = f.read().strip()

    assert actual_sha256 == expected_sha256, (
        f"gold_set_test.json has been modified! Expected {expected_sha256}, got {actual_sha256}"
    )
