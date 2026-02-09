import sqlite3
from typing import Dict, List, Any

class DatabaseExecutor:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def execute_query(self, query: str) -> Dict[str, Any]:
        """Executes a SQL query and returns results in a structured format."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            # Row factory helps returning rows as dicts if needed, 
            # but for tabular results, we'll keep it simple
            cursor = conn.cursor()
            cursor.execute(query)
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            if conn:
                conn.close()
