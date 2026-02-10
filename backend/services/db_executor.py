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
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Commit for non-SELECT statements
            if any(op in query.upper() for op in ["INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"]):
                conn.commit()

            rows = cursor.fetchall() if cursor.description else []
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # For DML statements, fetchall() is empty, so we use rowcount
            row_count = cursor.rowcount if not cursor.description else len(rows)
            
            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": row_count if row_count != -1 else len(rows)
            }
        except Exception as e:
            if conn:
                conn.rollback()
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            if conn:
                conn.close()

