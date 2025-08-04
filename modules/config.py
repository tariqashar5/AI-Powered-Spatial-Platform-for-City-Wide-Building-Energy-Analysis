# modules/config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# DB_PATH = "energy_map.db"
DB_PATH = r'D:\AI - KNU\Undergrad Project Mentoring (NineWatt)\new energy project\energy_map.db'
