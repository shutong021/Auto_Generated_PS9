# Data Inventory

## Raw data used in the partial replication

### 1. Transcript details
- Source file: `Transcript details.zip`
- Raw file inside zip: `kocfei0jhqc8raya.dta`
- Rows: 399,813
- Key fields used: `cik`, `companyid`, `transcriptid`, `mostimportantdateutc`
- Role: starting firm universe and metadata for linking transcript-text files

### 2. CRSP / Compustat-style quarterly panel
- Source file: `CRSP.zip`
- Raw file inside zip: `zbbfx668dr8a8hhd.dta`
- Rows: 221,806
- Columns: 687
- Key fields used: `cik`, `gind`
- Role: industry screen for Table 1

### 3. Capital IQ transcript text
- Source file: `Capital IQ transcript text.zip`
- Files inside zip: 5,956 JSON files
- Key fields used: `transcriptid`, `companyid`, `mostimportantdate`, `components`
- Role: reconstruct question-answer pairs for the accessible transcript-text subset

## Not available or not runnable in the shared environment
- `speaker detail` raw data were not available in the container.
- Helper modules `ling_features` and `kw_logic` were not included in the shared code package.
- Live API credentials were replaced with placeholders in the shared scripts.
