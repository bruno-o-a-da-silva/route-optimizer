from pathlib import Path

import pytest

from route_optimizer.bench import run_benchmark
from route_optimizer.cli import main


def test_benchmark_rows() -> None:
    rows = run_benchmark([1, 2], n=20)
    assert len(rows) == 2
    assert all(r.ls_km <= r.nn_km and r.km_saving_pct >= 0 for r in rows)
    assert rows == run_benchmark([1, 2], n=20)


def test_cli_solve(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["solve", "-n", "15", "--seed", "2"]) == 0
    out = capsys.readouterr().out
    assert "Synthetic example data" in out and "route 1: 0-" in out


def test_cli_bench_csv(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out_csv = tmp_path / "b.csv"
    assert main(["bench", "-n", "15", "--seeds", "2", "--csv", str(out_csv)]) == 0
    assert "mean distance saving" in capsys.readouterr().out
    assert len(out_csv.read_text().splitlines()) == 3
    assert main(["bench", "-n", "10", "--seeds", "1"]) == 0
