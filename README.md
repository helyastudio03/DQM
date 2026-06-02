# DQM — Data Quality Matching Engine

Entity Resolution and Data Matching Engine for identifying duplicates and links between datasets without modifying source data.

## Overview

DQM solves two core data quality pain points:

1. **Intra-source deduplication** — Identify duplicate records within a single dataset where records cannot be deleted due to downstream dependencies.
2. **Cross-source reconciliation** — Link records across isolated databases to a master referential.

Output: a probabilistic match map exported as CSV (no direct write-backs to source data).

## Stack

- **Backend**: Python FastAPI + RapidFuzz + pandas
- **Frontend**: React + TypeScript + Vite

## Quick Start

```bash
bash /home/user/DQM/start.sh
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## How It Works

### Matching Algorithm

1. **Normalization** — Lowercase, strip, remove special chars, collapse whitespace
2. **Blocking** — Records are grouped by a blocking key (first 3 chars of each mapped field) to avoid a full Cartesian product
3. **Fuzzy Scoring** — RapidFuzz `token_sort_ratio` on each configured field pair
4. **Aggregation** — Average score across all field pairs = final match_score (0–100)
5. **Filtering** — Only pairs with score >= 50 are returned

### Self-Comparison Mode

When analyzing a single dataset for internal duplicates:
- Self-matches (same ID) are excluded
- Only one direction is kept (A,B where A < B lexicographically)

## Workflow (5-Step Wizard)

1. **Sources** — Upload CSV, XLSX, or Parquet files
2. **Identifiers** — Select technical ID columns
3. **Mapping** — Configure field pairs to compare
4. **Execution** — Run the matching engine
5. **Results** — Review, filter, and export match pairs

## API Endpoints

- `POST /upload` — Upload a file, get session ID + metadata
- `POST /match` — Run matching, get results JSON
- `POST /export` — Run matching, download CSV
- `DELETE /session/{id}` — Purge session data
