import pandas as pd
from pathlib import Path

#Path to processed CSVs
ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"

def load_data():
    """Load both House and Senate CSVs into memory."""
    house = pd.read_csv(PROCESSED_DIR / "house_districts.csv")
    senate = pd.read_csv(PROCESSED_DIR / "senate_districts.csv")
    return house, senate

def get_district(chamber: str, district_number: int):
    """
    Return one row of data for a given chamber and sitrict number. 

    chamber: "house" or "senate"
    district_number: elg. 22
    """
    house, senate = load_data()

    if chamber.lower() == "house":
        df = house
    elif chamber.lower() == "senate":
        df = senate
    else:
        return None

    result = df[df["district"] == district_number]
    if result.empty:
        return None
    return result.iloc[0].to_dict()

if __name__ == "__main__":
    #Quick test
    data = get_district("house", 1)
    print(data)

#See data/README.md for usage example

