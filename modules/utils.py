# modules/utils.py

import re
import json
import os
import sqlite3

# Classification keywords
SQL_KEYWORDS = ["몇 개", "목록", "보여줘", "집계", "비율", "평균", "최대", "최소", "합계", "그래프", "시각화", "통계"]
HYBRID_KEYWORDS = ["이유", "특징", "원인", "차이", "패턴", "비교", "효율", "높은 이유", "어떤"]
RAG_KEYWORDS = ["무엇인가요", "왜", "설명", "알려줘", "경향", "차이는", "무엇", "어떻게", "특징", "이유", "패턴", "차이", "영향", "원인", "시간대", "시간별", "오전", "오후", "낮", "밤"]

# Classification
def is_explain_query(q: str) -> bool:
    return any(k in q for k in RAG_KEYWORDS) and not any(k in q for k in SQL_KEYWORDS)

def is_hybrid_query(q: str) -> bool:
    return any(k in q for k in HYBRID_KEYWORDS) and any(k in q for k in SQL_KEYWORDS)

def classify_query_type(question: str) -> str:
    if is_hybrid_query(question):
        return "Hybrid"
    if is_explain_query(question):
        return "RAG"
    return "SQL"

# SQL Cleaning and Fixing
import re

def postprocess_sql(sql: str) -> str:
    # Strip markdown formatting
    sql = sql.replace("```sql", "").replace("```", "").strip()

    # Normalize double quotes
    sql = sql.replace('""', '"')

    # Patch hallucinated or incorrect table names
    sql = sql.replace("FROM gas_daegu", "FROM energy_daegu")
    sql = sql.replace("FROM daegu", "FROM energy_daegu")

    # Fix and quote known special columns
    special_columns = [
        "사용량(KWh)", "연면적(m^2)", "건축면적(m^2)", "건폐율(%)", "용적률(%)",
        "세대수(세대)", "가구수(가구)", "높이(m)", "옥내기계식면적(m^2)",
        "옥외기계식면적(m^2)", "옥내자주식면적(m^2)", "옥외자주식면적(m^2)",
        "부속건축물면적(m^2)", "총동연면적(m^2)", "건물명"
    ]
    for col in special_columns:
        unquoted = re.sub(r'[\(\)\^%]', '', col)  # Remove special characters
        sql = re.sub(rf'(?<!")\b{re.escape(unquoted)}\b(?!")', f'"{col}"', sql)

    # Handle unquoted usage of 사용량
    sql = re.sub(r'(?<!")\b사용량\(KWh\)', '"사용량(KWh)"', sql)
    sql = re.sub(r'(?<!")\b사용량\b(?!")', '"사용량(KWh)"', sql)
    sql = sql.replace("e.사용량", 'e."사용량(KWh)"')

    # Fix Korean column names without quotes
    sql = re.sub(r'(?<!")\b도로명대지위치\b(?!")', '"도로명대지위치"', sql)
    sql = re.sub(r'(?<!")\b주용도코드명\b(?!")', '"주용도코드명"', sql)

    # Quote population fields like 2023년01월_총인구수
    sql = re.sub(r'\b(20\d{2}년\d{2}월_[가-힣A-Za-z0-9_]+)\b', r'"\1"', sql)

    # Fix SUM() and CASE statements
    sql = re.sub(r'SUM\((?<!")사용량(?!")\)', 'SUM("사용량(KWh)")', sql)
    sql = re.sub(r'SUM\(CASE([^\)]+)\)', r'SUM(CASE\1)', sql)  # Ensure SUM(CASE...) not broken

    # Remove lines with stray digits like `0` or invalid tokens
    sql = re.sub(r'^\s*\d+\s*$', '', sql, flags=re.MULTILINE)

    # Remove LIMIT 1 if added unnecessarily
    sql = re.sub(r'LIMIT\s+1\s*;?', '', sql, flags=re.IGNORECASE)

    # Fix trailing numeric or incomplete lines
    sql = re.sub(r"\s+0\s*;?\s*$", "", sql)
    sql = re.sub(r"[;,]\s*$", "", sql)

    # Filter SQL that ends mid-token (for safety)
    if sql.count('"') % 2 != 0:
        sql = sql.rsplit('"', 1)[0] + '"'  # close unmatched quote

    # Remove accidental trailing numbers or tokens after ORDER BY
    sql = re.sub(r'(ORDER BY [\w\."()]+(?: ASC| DESC)?)(\s+\d+\s*)$', r'\1', sql, flags=re.IGNORECASE)

    # Final clean-up
    return sql.strip("; ")

# Schema utils
def load_schema_string(schema_path="db_schema.json") -> str:
    if not os.path.exists(schema_path):
        print("❌ db_schema.json not found")
        return "스키마를 찾을 수 없습니다."

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    lines = []
    for table, columns in schema.items():
        lines.append(f"테이블: {table}")
        for col in columns:
            if isinstance(col, dict):
                lines.append(f" - {col['column_name']} ({col['type']})")
            else:
                lines.append(f" - {col}")
        lines.append("")
    return "\n".join(lines)

def get_schema_dict(db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
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
    return schema
