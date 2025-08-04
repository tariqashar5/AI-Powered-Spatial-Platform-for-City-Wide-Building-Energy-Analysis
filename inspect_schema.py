import sqlite3
import json

conn = sqlite3.connect("db/energy_map.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

schema = {}

for table in tables:
    cursor.execute(f"PRAGMA table_info({table});")
    columns = cursor.fetchall()
    schema[table] = [
        {
            "column_name": col[1],
            "type": col[2],
            "notnull": bool(col[3]),
            "default": col[4],
            "pk": bool(col[5])
        }
        for col in columns
    ]

conn.close()

with open("db_schema.json", "w", encoding="utf-8") as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)

print("✅ Saved schema to db_schema.json")

