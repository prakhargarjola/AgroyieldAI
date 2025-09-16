import requests
import pandas as pd
from tqdm import tqdm


INPUT_FILE = "dataset/up_lat_long.csv"   
OUTPUT_FILE = "dataset/up_weather_data2.csv"      
START_DATE = "20000101"                  
END_DATE = "20201231"


def get_weather_data(lat, lon, start=START_DATE, end=END_DATE, district="Unknown"):
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters=T2M,T2M_MAX,T2M_MIN,RH2M,PRECTOT"
        f"&community=AG&longitude={lon}&latitude={lat}"
        f"&start={start}&end={end}&format=JSON"
    )

    try:
        r = requests.get(url, timeout=30).json()
        data = r["properties"]["parameter"]
    except Exception as e:
        print(f"Error fetching data for {district}: {e}")
        return pd.DataFrame()

    records = []
    for date in data["T2M"].keys():
        records.append({
            "date": date,
            "district": district,
            "lat": lat,
            "lon": lon,
            "temp_avg": data["T2M"][date],
            "temp_max": data["T2M_MAX"][date],
            "temp_min": data["T2M_MIN"][date],
            "humidity": data["RH2M"][date] if "RH2M" in data else None,
            "rainfall": data["PRECTOTCORR"][date] if "PRECTOTCORR" in data else None
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    
    df_coords = pd.read_csv(INPUT_FILE)

    all_dfs = []

    for _, row in tqdm(df_coords.iterrows(), total=len(df_coords)):
        df_weather = get_weather_data(
            row["Latitude"], row["Longitude"], 
            start=START_DATE, end=END_DATE, 
            district=row["District"]
        )
        if not df_weather.empty:
            all_dfs.append(df_weather)

    final_df = pd.concat(all_dfs, ignore_index=True)

    
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Weather dataset saved as {OUTPUT_FILE}")
