import pandas as pd
import sqlite3

building_df = pd.read_csv("data/building_daegu.csv", low_memory=False)
energy_df = pd.read_csv("data/energy_daegu.csv", low_memory=False)

building_df = building_df.rename(columns={"건축물ID": "building_id"})
energy_df = energy_df.rename(columns={"건축물ID": "building_id"})

merged_df = pd.merge(energy_df, building_df, on="PNU", how="inner")

conn = sqlite3.connect("db/energy_map.db")
merged_df.to_sql("energy_merged", conn, if_exists="replace", index=False)
conn.close()
