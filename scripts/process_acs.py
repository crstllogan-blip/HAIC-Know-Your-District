"""
Starter script to download and process ACS 2020-2024 5-year
House and Senate legislative district data for Hawaii.

Run from the repo root:
    python3 scripts/process_acs.py

Outputs clean CSVs to data/processed/
"""

import re
from typing import Optional

import requests
import pandas as pd
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Create directories
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Source URLs (from Hawaii State Data Center)
HOUSE_URL = "https://files.hawaii.gov/dbedt/census/acs/acs2024/5yr/acs2024_5yr_house_hi.xlsx"
SENATE_URL = "https://files.hawaii.gov/dbedt/census/acs/acs2024/5yr/acs2024_5yr_senate_hi.xlsx"

# Key labels we want to extract (exact or partial matches from column 0)
KEY_LABELS = {
    "Population 16 years and over": "pop_16_plus",
    "In labor force": "in_labor_force",
    "Median household income (dollars)": "median_hh_income",
    "Mean household income (dollars)": "mean_hh_income",
    "Per capita income (dollars)": "per_capita_income",
    "Median family income (dollars)": "median_family_income",
    "Percentage of families whose income in the past 12 months is below the poverty level": "pct_families_poverty",
    "Percentage of people whose income in the past 12 months is below the poverty level": "pct_people_poverty",
    "Percentage of people 18 years and over whose income in the past 12 months is below the poverty level": "pct_18plus_poverty",
    "Percentage of people 65 years and over whose income in the past 12 months is below the poverty level": "pct_65plus_poverty",
}

def download_file(url: str, dest: Path) -> None:
    """Download a file if it does not already exist."""
    if dest.exists():
        print(f"Already exists: {dest}")
        return
    print(f"Downloading {url} ...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    dest.write_bytes(response.content)
    print(f"Saved to {dest}")

def extract_district_number(name: str) -> Optional[int]:
    """Extract the numeric district ID from a name like 'State House District 22 (2024); Hawaii'."""
    if not isinstance(name, str):
        return None
    match = re.search(r"District\s+(\d+)", name, re.IGNORECASE)
    return int(match.group(1)) if match else None

def extract_key_metrics(excel_path: Path, chamber: str) -> pd.DataFrame:
    """
    Parse the wide-format DP03 sheet and extract key metrics per district.
    """
    print(f"Reading {excel_path} ...")
    df = pd.read_excel(excel_path, sheet_name="DP03", header=None)

    # Row 0 contains district names in columns 1, 5, 9, 13, ...
    district_cols = []
    for col in range(1, df.shape[1], 4):
        district_name = df.iloc[0, col]
        if isinstance(district_name, str) and "District" in district_name:
            district_cols.append((col, district_name))

    print(f"  Found {len(district_cols)} districts")

    records = []
    for start_col, district_name in district_cols:
        district_num = extract_district_number(district_name)
        record = {
            "chamber": chamber,
            "district": district_num,
            "district_name": district_name,
        }

        # For each key label, find the matching row and grab Estimate + MOE + Percent
        for label, field in KEY_LABELS.items():
            # Find the row where column 0 contains the label
            mask = df[0].astype(str).str.contains(re.escape(label), case=False, na=False)
            matching_rows = df[mask]
            if matching_rows.empty:
                record[f"{field}_estimate"] = None
                record[f"{field}_moe"] = None
                record[f"{field}_percent"] = None
                continue

            row_idx = matching_rows.index[0]
            # Columns for this district: start_col = Estimate, +1 = MOE, +2 = Percent, +3 = Percent MOE
            record[f"{field}_estimate"] = df.iloc[row_idx, start_col]
            record[f"{field}_moe"] = df.iloc[row_idx, start_col + 1]
            record[f"{field}_percent"] = df.iloc[row_idx, start_col + 2]

        records.append(record)

    result = pd.DataFrame(records)
    print(f"  Extracted {len(result)} rows")
    return result

def main():
    house_raw = RAW_DIR / "acs2024_5yr_house_hi.xlsx"
    senate_raw = RAW_DIR / "acs2024_5yr_senate_hi.xlsx"

    download_file(HOUSE_URL, house_raw)
    download_file(SENATE_URL, senate_raw)

    house_df = extract_key_metrics(house_raw, "house")
    senate_df = extract_key_metrics(senate_raw, "senate")

    house_out = PROCESSED_DIR / "house_districts.csv"
    senate_out = PROCESSED_DIR / "senate_districts.csv"

    house_df.to_csv(house_out, index=False)
    senate_df.to_csv(senate_out, index=False)

    print(f"\nWrote {house_out}")
    print(f"Wrote {senate_out}")
    print("\nSample of house data:")
    print(house_df.head(3).to_string())
    print("\nDone. You can now open the CSVs in data/processed/ or load them in your agent.")

if __name__ == "__main__":
    main()
