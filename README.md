# PS7 Replication Repository Skeleton for de Kok (2025)

This repository contains the materials needed to reproduce the **partial raw-data replication** that was executed in the container for Problem Set 7.

## What is in this repo

- `code_original/`: the original scripts supplied in the local replication package.
- `scripts/`: Python scripts that translate the deterministic sample-construction workflow into a runnable form.
- `output/`: generated outputs from the actual execution, including the partial Table 1 comparison and a 1,000-row Q&A sample.
- `notes/`: execution log, data inventory, and replication-results summary.
- `data_raw/`: placeholder folders showing where proprietary raw data should be placed locally.

## Recommended directory structure

```text
ps7_dekok_replication/
├── README.md
├── requirements.txt
├── code_original/
├── scripts/
├── output/
├── notes/
└── data_raw/
    ├── transcript_details/
    ├── capital_iq_text/
    ├── crsp/
    └── speaker_detail/
```

## What to put in each folder

### `code_original/`
Put the original shared scripts here exactly as received:
- `sample construction code.do`
- `Gow et al 2021.py`
- `Spark Pro(or Max).py`
- `Keyword+Spark Max.py`

### `data_raw/transcript_details/`
Place the extracted Stata file from `Transcript details.zip` here:
- `kocfei0jhqc8raya.dta`

### `data_raw/crsp/`
Place the extracted Stata file from `CRSP.zip` here:
- `zbbfx668dr8a8hhd.dta`

### `data_raw/capital_iq_text/`
Place the zip file `Capital IQ transcript text.zip` here, or extract its JSON contents here and adjust the script path if needed.

### `data_raw/speaker_detail/`
Leave empty unless speaker-level data become available later.

### `scripts/`
Use these scripts to reproduce the deterministic part of the workflow:
- `01_build_industry_screen.py`: reproduces the firm-level industry screen.
- `02_build_available_qna_sample.py`: links the accessible transcript-text subset and rebuilds Q&A pairs.
- `03_script_diagnostics.py`: shows why the original Python scripts are not directly runnable in the shared environment.

### `output/`
Store all generated outputs here. The current skeleton already contains:

To keep the repository small and GitHub-friendly, the full 100k+ row filtered Q&A files are **not** committed here. They can be regenerated locally by rerunning `scripts/02_build_available_qna_sample.py`.
- `table1_partial_replication_comparison.csv`
- `sample_construction_summary.json`
- `qna_pairs_after_char_filters.csv`
- `qna_pairs_after_word_filters.csv`
- `qna_sample_1000_char_filter.csv`
- `original_script_diagnostics.csv`

### `notes/`
Store the write-up support files here:
- `execution_log.md`
- `replication_results.md`
- `data_inventory.md`

## How to run the partial replication

1. Create a fresh Python environment and install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Put the proprietary raw data in the `data_raw/` subfolders.
3. Run the industry screen:
   ```bash
   python scripts/01_build_industry_screen.py
   ```
4. Run the Q&A reconstruction on the accessible transcript-text subset:
   ```bash
   python scripts/02_build_available_qna_sample.py
   ```
5. Run the diagnostics for the original Python scripts:
   ```bash
   python scripts/03_script_diagnostics.py
   ```

## What this run achieved

This execution reproduced the first stage of Table 1 exactly:
- 12,614 starting firms
- 5,626 firms after the industry screen

The execution also built a partial Q&A sample from the accessible transcript-text subset:
- 141 screened firms represented in the uploaded text subset
- 5,375 calls with at least five question exchanges
- 101,072 Q&A pairs after applying the code-as-written character thresholds

## What this run could not do

The non-answer evaluation scripts could not be rerun end-to-end because the shared package is incomplete:
- `ling_features` is missing
- `kw_logic` is missing
- the Spark scripts use Windows-specific paths
- the Spark scripts contain placeholder API credentials instead of live keys

## How to upload this to GitHub

1. Create a new GitHub repository.
2. Upload this folder structure.
3. Keep raw proprietary data out of the repository if redistribution is not allowed.
4. Commit the generated `output/` summaries and the `notes/` files.
5. In the final PS7 answer, paste your GitHub repository link in Question 3.3.
