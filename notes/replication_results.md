# Replication Results Summary

## What was successfully reproduced
The agent successfully reproduced the firm-level industry screen from raw data. Using the transcript-details file and CRSP/Compustat-style industry codes, the run recovered exactly 12,614 starting firms and exactly 5,626 firms after excluding missing-industry firms and sectors 40 and 55.

The agent also successfully built a Q&A-level dataset from the uploaded transcript-text JSON files. Because the accessible transcript-text subset covers only 141 screened firms, this is a partial rather than full replication. Within that subset, the agent linked 5,953 JSON files to screened firms, identified 5,375 calls with at least five question exchanges, and reconstructed 101,072 Q&A pairs after applying the code-as-written length filters.

## Main discrepancy relative to the target Table 1
The target final sample in the team table is 5,471 firms and 166,848 Q&A pairs. The agent could not reach those totals because the uploaded transcript-text subset covers only 141 screened firms, not the full underlying text universe. The gap is therefore driven by data coverage, not by a failure in the deterministic firm-level screen.

## Additional discrepancy found during execution
The Stata code uses character counts (`ustrlen`) for the final thresholds, while the team table describes the thresholds in words. On the accessible subset, the code-as-written character thresholds yield 101,072 Q&A pairs, while the documented word thresholds yield 73,296. This is a real documentation-versus-code discrepancy that should be disclosed in the write-up.

## Why the model-comparison tables were not rerun
The uploaded Python scripts for the classification stage are not self-contained. One script requires `ling_features`, another requires `kw_logic`, and the Spark scripts also depend on Windows-specific file paths and placeholder API credentials. For that reason, the agent could not rerun the non-answer evaluation tables from raw data in the current shared environment.
