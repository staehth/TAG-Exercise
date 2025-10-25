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

def generate_schema_str(engine: Engine) -> str:
    """Generate a schema description string for all tables in the connected SQLite DB."""
    insp = inspect(engine)
    schema_lines = []
    for table_name in insp.get_table_names():
        columns = [col["name"] for col in insp.get_columns(table_name)]
        schema_lines.append(f"Table {table_name}, columns = {columns}")
    return "\n".join(schema_lines)

# Create a global SCHEMA_STR for imports
SCHEMA_STR = generate_schema_str(engine)

# --- 3. SQL Execution Function ---
def run_sql(engine: Engine, sql: str) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql_query(sql, conn)
    return df