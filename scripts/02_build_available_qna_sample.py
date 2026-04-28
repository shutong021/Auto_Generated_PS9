"""Translate the sample-construction logic into Python for the accessible transcript-text subset.

The available raw text data do not reproduce the author's full proprietary text universe.
This script therefore builds a *partial* Q&A sample from the uploaded Capital IQ transcript
JSON files and links them to screened firms via companyid + event date.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import json
import re
import zipfile
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT_DTA = ROOT / "data_raw" / "transcript_details" / "kocfei0jhqc8raya.dta"
TEXT_ZIP = ROOT / "data_raw" / "capital_iq_text" / "Capital IQ transcript text.zip"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)

# This helper file is produced by script 01.
INDUSTRY_MAP = OUT_DIR / "industry_screen_firm_map.csv"


def build_company_date_map(trans: pd.DataFrame, clean_firms: set[str]) -> tuple[dict[tuple[float, object], str], int]:
    trans = trans.copy()
    trans["clean_cik"] = trans["cik"].where(trans["cik"].isin(clean_firms))
    company_mode: dict[float, str] = {}
    for companyid, vals in trans[["companyid", "clean_cik"]].dropna().groupby("companyid")["clean_cik"]:
        company_mode[companyid] = Counter(vals.astype(str)).most_common(1)[0][0]

    out: dict[tuple[float, object], str] = {}
    ambiguous = 0
    for (companyid, date), vals in trans[["companyid", "date", "clean_cik"]].dropna().groupby(["companyid", "date"])["clean_cik"]:
        uniq = sorted(set(vals.astype(str)))
        if len(uniq) == 1:
            out[(companyid, date)] = uniq[0]
        elif len(uniq) > 1:
            chosen = company_mode.get(companyid, uniq[0])
            if chosen not in uniq:
                chosen = uniq[0]
            out[(companyid, date)] = chosen
            ambiguous += 1
    return out, ambiguous


def main() -> None:
    firm_map = pd.read_csv(INDUSTRY_MAP, dtype={"cik": str, "gind": str})
    clean_firms = set(firm_map.loc[firm_map["keep"] == True, "cik"])

    trans = pd.read_stata(TRANSCRIPT_DTA)[["companyid", "mostimportantdateutc", "cik"]]
    trans["cik"] = trans["cik"].astype(str).str.strip()
    trans = trans[(trans["cik"].notna()) & (trans["cik"] != "")].copy()
    trans["date"] = pd.to_datetime(trans["mostimportantdateutc"]).dt.date

    company_date_map, ambiguous = build_company_date_map(trans, clean_firms)

    meta_rows = []
    qa_rows = []
    with zipfile.ZipFile(TEXT_ZIP) as zf:
        for name in zf.namelist():
            data = json.loads(zf.read(name))
            companyid = data.get("companyid")
            date = pd.to_datetime(data.get("mostimportantdate")).date() if data.get("mostimportantdate") else None
            cik = company_date_map.get((companyid, date))
            is_clean = cik in clean_firms if cik is not None else False
            meta_rows.append(
                {
                    "json_transcriptid": int(data.get("transcriptid")),
                    "companyid": companyid,
                    "date": str(date) if date else None,
                    "assigned_cik": cik,
                    "is_clean1": bool(is_clean),
                    "n_components_total": len(data.get("components", [])),
                }
            )
            if not is_clean:
                continue

            comps = [
                c for c in data.get("components", [])
                if c.get("componenttypename") in ("Question", "Answer", "Question and Answer Operator Message")
            ]
            comps.sort(key=lambda c: c.get("componentorder") if c.get("componentorder") is not None else 10**9)

            qid = 0
            kept = []
            for c in comps:
                if c.get("componenttypename") == "Question":
                    qid += 1
                if qid > 0:
                    kept.append((qid, c.get("componenttypename"), (c.get("text") or "").strip()))
            if qid < 5:
                continue

            q_text = {}
            a_parts: dict[int, list[str]] = defaultdict(list)
            for qnum, typ, text in kept:
                if typ == "Question" and qnum not in q_text:
                    q_text[qnum] = text
                elif typ == "Answer":
                    a_parts[qnum].append(text)

            for qnum, question in q_text.items():
                answer = " ".join([t for t in a_parts.get(qnum, []) if t]).strip()
                qa_rows.append(
                    {
                        "cik": cik,
                        "json_transcriptid": int(data.get("transcriptid")),
                        "companyid": companyid,
                        "date": str(date) if date else None,
                        "qid": qnum,
                        "question": question,
                        "answer": answer,
                        "q_char_len": len(question),
                        "a_char_len": len(answer),
                        "qa_char_len": len(question + answer),
                        "q_word_len": len([w for w in re.split(r"\\s+", question) if w]),
                        "a_word_len": len([w for w in re.split(r"\\s+", answer) if w]),
                        "qa_word_len": len([w for w in re.split(r"\\s+", (question + " " + answer).strip()) if w]),
                    }
                )

    meta_df = pd.DataFrame(meta_rows)
    qa_df = pd.DataFrame(qa_rows)
    char_f = qa_df[(qa_df["q_char_len"] >= 30) & (qa_df["a_char_len"] >= 10) & (qa_df["qa_char_len"] >= 75)].copy()
    word_f = qa_df[(qa_df["q_word_len"] >= 30) & (qa_df["a_word_len"] >= 10) & (qa_df["qa_word_len"] >= 75)].copy()
    sample = char_f.sample(n=min(1000, len(char_f)), random_state=42).sort_values(["cik", "json_transcriptid", "qid"])

    meta_df.to_csv(OUT_DIR / "available_transcript_text_inventory.csv", index=False)
    char_f.to_csv(OUT_DIR / "qna_pairs_after_char_filters.csv", index=False)
    word_f.to_csv(OUT_DIR / "qna_pairs_after_word_filters.csv", index=False)
    sample.to_csv(OUT_DIR / "qna_sample_1000_char_filter.csv", index=False)

    summary = {
        "available_json_files": int(len(meta_df)),
        "available_json_files_linked_to_clean1_firms": int(meta_df["is_clean1"].sum()),
        "linked_clean1_firms_in_json_subset": int(meta_df.loc[meta_df["is_clean1"], "assigned_cik"].nunique()),
        "transcripts_with_at_least_5_questions": int(qa_df["json_transcriptid"].nunique()),
        "firms_with_at_least_5_questions": int(qa_df["cik"].nunique()),
        "qna_pairs_after_char_filter": int(len(char_f)),
        "firms_after_char_filter": int(char_f["cik"].nunique()),
        "transcripts_after_char_filter": int(char_f["json_transcriptid"].nunique()),
        "qna_pairs_after_word_filter": int(len(word_f)),
        "firms_after_word_filter": int(word_f["cik"].nunique()),
        "transcripts_after_word_filter": int(word_f["json_transcriptid"].nunique()),
        "ambiguous_companyid_date_groups_with_multiple_clean_cik": int(ambiguous),
    }
    pd.Series(summary).to_json(OUT_DIR / "available_qna_subset_summary.json", indent=2)
    print(summary)


if __name__ == "__main__":
    main()
