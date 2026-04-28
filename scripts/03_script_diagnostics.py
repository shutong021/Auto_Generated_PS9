"""Record why the original Python scripts are not directly runnable in the shared environment."""

from __future__ import annotations

from pathlib import Path
import subprocess
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code_original"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)

SCRIPTS = [
    "Gow et al 2021.py",
    "Spark Pro(or Max).py",
    "Keyword+Spark Max.py",
]


def main() -> None:
    rows = []
    for script in SCRIPTS:
        proc = subprocess.run(
            ["python", str(CODE_DIR / script)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        rows.append(
            {
                "script": script,
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-500:],
                "stderr_tail": proc.stderr[-1000:],
            }
        )
    pd.DataFrame(rows).to_csv(OUT_DIR / "original_script_diagnostics.csv", index=False)
    print(pd.DataFrame(rows))


if __name__ == "__main__":
    main()
