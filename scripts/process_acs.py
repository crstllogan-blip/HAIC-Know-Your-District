"""
Starter script to download and process ACS 2020-2024 5-year
House and Senate legislative district data for Hawaii.

Run from the repo root:
    python scripts/process_acs.py

Outputs clean CSVs to data/processed/
"""

import os
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

def extract_key_metrics(excel_path: Path, chamber: str) -> pd.DataFrame:
    """
    Extract a small set of useful columns from the DP03 sheet.
    Expand this function as you identify more columns you need.
    """
    print(f"Reading {excel_path} ...")
    # DP03 is typically the third sheet (0-indexed: 2)
    df = pd.read_excel(excel_path, sheet_name="DP03", header=None)

    # The exact layout can vary. This is a simplified starter that
    # looks for district identifiers and a few common metrics.
    # You will likely need to inspect the sheet and adjust the row/column logic.

    # Example: find the header row that contains "District" or similar
    # (This is intentionally simple — refine after you open the file once.)
    records = []

    # Placeholder logic — replace with real parsing once you examine the sheet
    # For now we just confirm the file opens and note the shape.
    print(f"  Sheet shape: {df.shape}")
    print(f"  First 5 rows (preview):")
    print(df.head().to_string())

    # TODO: Implement real extraction of:
    # - District number / name
    # - Median household income
    # - Poverty rate (overall and 65+)
    # - Housing cost burden
    # - etc.
    # Save the raw preview so you can inspect it.
    preview_path = PROCESSED_DIR / f"{chamber}_dp03_preview.csv"
    df.head(20).to_csv(preview_path, index=False)
    print(f"  Preview saved to {preview_path}")

    # Return an empty DataFrame for now; fill it in after inspection.
    return pd.DataFrame()

def main():
    house_raw = RAW_DIR / "acs2024_5yr_house_hi.xlsx"
    senate_raw = RAW_DIR / "acs2024_5yr_senate_hi.xlsx"

    download_file(HOUSE_URL, house_raw)
    download_file(SENATE_URL, senate_raw)

    # Process each file
    house_df = extract_key_metrics(house_raw, "house")
    senate_df = extract_key_metrics(senate_raw, "senate")

    # Once extraction is working, uncomment these:
    # house_df.to_csv(PROCESSED_DIR / "house_districts.csv", index=False)
    # senate_df.to_csv(PROCESSED_DIR / "senate_districts.csv", index=False)
    # print("Processed CSVs written to data/processed/")

    print("\nDone. Open the preview CSVs in data/processed/ to see the sheet layout,")
    print("then update the extract_key_metrics() function to pull the columns you need.")

if __name__ == "__main__":
    main()
