# Data Directory

This folder holds processed, analysis-ready datasets for the HAIC Know Your District agent.

## Structure

```
data/
├── raw/                  # Optional: downloaded source files (not committed by default)
│   ├── acs_house.xlsx
│   └── acs_senate.xlsx
├── processed/            # Clean, tidy tables the agent will query
│   ├── house_districts.csv
│   └── senate_districts.csv
└── README.md             # This file
```

## Sources

See `../data_sources.md` for the full list of upstream sources and links.

## How to generate the processed files

Run the processing script from the repo root:

```bash
python scripts/process_acs.py
```

The script will:
1. Download the latest ACS 2020–2024 5-year House and Senate Excel files from the Hawaii State Data Center.
2. Extract key columns from the DP03 (and related) sheets.
3. Write clean CSVs into `data/processed/`.

## Notes

- Raw Excel files are large and are not committed by default (see `.gitignore`).
- Always cite the original source (ACS table ID, year, and geography) when the agent returns a number.
- Margins of error should be preserved or at least noted.
