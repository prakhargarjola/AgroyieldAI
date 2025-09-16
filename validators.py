import pandas as pd

district_coords = pd.read_csv("dataset/up_lat_long.csv")

VALID_DISTRICTS = set(district_coords["District"].str.lower().tolist())

def validate_district(district: str) -> bool:
    """Check if district is valid"""
    return district.lower() in VALID_DISTRICTS
