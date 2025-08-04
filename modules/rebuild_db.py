import sqlite3
import pandas as pd
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)

building_df = pd.read_csv("data/building_daegu.csv", low_memory=False)
energy_df = pd.read_csv("data/energy_daegu.csv")
population_df = pd.read_csv("data/population.csv")

# Optional: rename columns to match what the LLM expects
building_df = building_df.rename(columns={"건축물ID": "building_id", "연면적(m^2)": "total_area"})
energy_df = energy_df.rename(columns={"건축물ID": "building_id", "사용년월": "year_month"})
population_df = population_df.rename(columns={"행정동코드": "region_id", "총인구수": "population"})

building_df.to_sql("building_daegu", conn, if_exists="replace", index=False)
energy_df.to_sql("energy_daegu", conn, if_exists="replace", index=False)
population_df.to_sql("population", conn, if_exists="replace", index=False)

conn.close()
print("✅ energy_map.db rebuilt with required tables.")
