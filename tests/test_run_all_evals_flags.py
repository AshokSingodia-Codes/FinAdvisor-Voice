import subprocess
import sys


def test_run_all_evals_flags():
    res = subprocess.run(
        [sys.executable, "scripts/run_all_evals.py", "--help"],
        capture_output=True,
        text=True,
        check=True
    )
    help_text = res.stdout
    assert "--split" in help_text
    assert "--retrieval" in help_text
    assert "--router" in help_text
    assert "--faithfulness" in help_text
    assert "--trap" in help_text
