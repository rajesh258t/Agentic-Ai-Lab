import sqlite3
import pandas as pd

def run_query(sql_query):
    conn = sqlite3.connect("students.db")
    
    try:
        df = pd.read_sql_query(sql_query, conn)
        return df
    
    except Exception as e:
        return str(e)
    
    finally:
        conn.close()