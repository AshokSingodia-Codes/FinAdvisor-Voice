import hashlib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_router_holdout_v2_frozen():
    v2_path = os.path.join(ROOT, "tests", "eval", "router_holdout_v2.json")
    sha_path = os.path.join(ROOT, "tests", "eval", "router_holdout_v2.sha256")

    assert os.path.exists(v2_path), "router_holdout_v2.json missing"
    assert os.path.exists(sha_path), "router_holdout_v2.sha256 missing"

    with open(v2_path, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()

    with open(sha_path, "r", encoding="utf-8") as f:
        expected_hash = f.read().strip()

    assert actual_hash == expected_hash, (
        f"router_holdout_v2.json has been modified! Expected {expected_hash}, got {actual_hash}"
    )
