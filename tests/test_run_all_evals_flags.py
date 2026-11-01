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
    assert "Not implemented in this runner" in help_text


def test_run_all_evals_unimplemented_flags_exit_nonzero():
    for flag in ["--retrieval", "--faithfulness", "--trap"]:
        res = subprocess.run(
            [sys.executable, "scripts/run_all_evals.py", "--split", "dev", flag],
            capture_output=True,
            text=True
        )
        assert res.returncode != 0
        assert "not implemented in this runner; run: python -m tests.eval." in res.stdout
