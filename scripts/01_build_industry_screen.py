"""Build the firm-level industry screen used in the partial replication.

This script reproduces the first stage of Table 1 from the raw Transcript Details
and CRSP/Compustat-style quarterly panel. It keeps only firms with non-missing
industry information and excludes sector prefixes 40 and 55.
"""

from __future__ import annotations

import pickle
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT_DTA = ROOT / "data_raw" / "transcript_details" / "kocfei0jhqc8raya.dta"
CRSP_DTA = ROOT / "data_raw" / "crsp" / "zbbfx668dr8a8hhd.dta"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)


def build_crsp_cik_gind_map(crsp_path: Path) -> dict[str, str]:
    reader = pd.read_stata(crsp_path, iterator=True)
    cik_to_counts: dict[str, dict[str, int]] = {}
    while True:
        try:
            chunk = reader.read(50_000)
        except StopIteration:
            break
        if chunk.empty:
            break
        for cik, gind in zip(chunk["cik"], chunk["gind"]):
            if pd.isna(cik):
                continue
            cik_str = str(cik).strip()
            if not cik_str:
                continue
            gind_str = "" if pd.isna(gind) else str(gind).strip()
            inner = cik_to_counts.setdefault(cik_str, {})
            inner[gind_str] = inner.get(gind_str, 0) + 1

    out: dict[str, str] = {}
    for cik, counts in cik_to_counts.items():
        nonempty = [(g, c) for g, c in counts.items() if g]
        if not nonempty:
            out[cik] = ""
            continue
        nonempty.sort(key=lambda kv: (-kv[1], kv[0]))
        out[cik] = nonempty[0][0]
    return out


def main() -> None:
    trans = pd.read_stata(TRANSCRIPT_DTA)[["cik"]]
    trans["cik"] = trans["cik"].astype(str).str.strip()
    firms = trans[(trans["cik"].notna()) & (trans["cik"] != "")].drop_duplicates().copy()

    mapping = build_crsp_cik_gind_map(CRSP_DTA)
    firms["gind"] = firms["cik"].map(mapping)
    firms["keep"] = (
        firms["gind"].notna()
        & (firms["gind"] != "")
        & ~firms["gind"].astype(str).str[:2].isin(["40", "55"])
    )

    summary = {
        "starting_firms": int(firms["cik"].nunique()),
        "firms_after_industry_screen": int(firms.loc[firms["keep"], "cik"].nunique()),
        "excluded_firms": int(firms["cik"].nunique() - firms.loc[firms["keep"], "cik"].nunique()),
    }

    firms.to_csv(OUT_DIR / "industry_screen_firm_map.csv", index=False)
    pd.Series(summary).to_json(OUT_DIR / "industry_screen_summary.json", indent=2)
    print(summary)


if __name__ == "__main__":
    main()
