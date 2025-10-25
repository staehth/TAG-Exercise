import os
import json
import pandas as pd
from openai import OpenAI
from sqlalchemy.engine import Engine
from .database import run_sql # Import the execution function

import os
import json
import pandas as pd
from openai import OpenAI
from sqlalchemy.engine import Engine
from .database import run_sql # Import the execution function

# --- 1. Data Formatting ---
def preview_rows_for_prompt(df: pd.DataFrame, max_rows: int = 30, max_cols: int = 12) -> str:
    """Turn a (small) slice of the DataFrame into a compact markdown table for the LLM prompt."""
    if df is None or df.empty:
        return "(no rows)"
    # Trim super-wide tables
    df_small = df.copy()
    if df_small.shape[1] > max_cols:
        df_small = df_small.iloc[:, :max_cols]
    # Show at most N rows
    df_small = df_small.head(max_rows)
    # Convert to nice markdown table without index
    return df_small.to_markdown(index=False)


# --- 2. LLM Generation Functions ---
def generate_sql_openai(question: str, schema: str, model: str = None) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _SYSTEM_PROMPT = """You convert natural-language questions into read-only SQLite SQL.
                        Rules:
                        - Output only a JSON object like: {"sql": "..."}.
                        - Use SELECT queries only. Never write INSERT/UPDATE/DELETE/DDL.
                        - Prefer clear column aliases and LIMIT if the result could be large.
                        - The target dialect is SQLite.
                    """
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role":"system","content": _SYSTEM_PROMPT},
            {"role":"user","content": f"schema:\n{schema}\n\nquestion: {question}"},
        ],
    )
    payload = json.loads(resp.choices[0].message.content)
    return payload["sql"]
    
def build_answer_prompt(question: str, sql: str, df: pd.DataFrame) -> list[dict]:
    rows_md = preview_rows_for_prompt(df)
    ANSWER_SYSTEM = """You are a helpful data assistant.
                        Given a user's question, the SQL that was executed (read-only), and the resulting rows,
                        write a concise factual answer in natural language.

                        Rules:
                        - Only use the values that actually appear in the provided rows.
                        - If the result looks incomplete or ambiguous, say so briefly and suggest a clarifying follow-up.
                        - Prefer bullet points or a short paragraph. Keep it tight.
                        - If there are numbers, include them exactly as shown (do not round unless asked).
                    """
    user_content = f"""Question:
                        {question}

                        SQL:
                        {sql}

                        Rows (first few shown):
                        {rows_md}
                    """
    return [
        {"role": "system", "content": ANSWER_SYSTEM},
        {"role": "user", "content": user_content},
    ]

def llm_answer_openai(question: str, sql: str, df: pd.DataFrame, model: str = None) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    msgs = build_answer_prompt(question, sql, df)
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=msgs,
    )
    return resp.choices[0].message.content.strip()
    


# --- 4. Full Pipeline ---

def text_to_sql_qa(question, schema, engine, model="gpt-4o-mini"):
    sql = generate_sql_openai(question, schema, model)
    df = run_sql(engine, sql)
    answer = llm_answer_openai(question, sql, df, model)
    return answer