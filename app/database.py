import os
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

# --- 1. Database Setup ---

# Assumes the notebook's setup code is run once to create the database file
DB_PATH = Path("demo.db")
DB_URI = f"sqlite:///file:{DB_PATH.resolve()}?mode=ro&uri=true"
engine: Engine = create_engine(DB_URI, connect_args={"uri": True})


# --- 2. Schema Extraction (for LLM Grounding) ---


# --- 3. SQL Execution Function ---
