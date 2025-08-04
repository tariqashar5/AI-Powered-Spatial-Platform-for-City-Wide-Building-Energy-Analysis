# modules/db_executor.py

import sqlite3
import pandas as pd
import os
import traceback

# Use consistent DB path logic
DB_PATH = os.path.abspath("D:/AI - KNU/Undergrad Project Mentoring (NineWatt)/new energy project/energy_map.db")

def execute_sql_query(sql: str) -> pd.DataFrame:
    print("🔥 Current Working Dir:", os.getcwd())
    print("🛠 Attempting DB path:", DB_PATH)
    print("✅ File exists:", os.path.exists(DB_PATH))
    print("📂 Is file a file:", os.path.isfile(DB_PATH))
    print("📌 Attempting DB path:", DB_PATH)

    try:
        conn = sqlite3.connect(DB_PATH)
        print("✅ Connection opened")
        print("🧠 Executing SQL:", sql)
        df = pd.read_sql_query(sql, conn)
        print("📊 Rows fetched:", len(df))
        return df
    except Exception as e:
        print("❌ SQL execution failed!")
        traceback.print_exc()
        raise e
    finally:
        conn.close()
