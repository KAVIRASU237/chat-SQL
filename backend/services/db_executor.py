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
            
            upper_query = query.upper()
            if any(op in upper_query for op in ["INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"]):
                conn.commit()

            rows = cursor.fetchall() if cursor.description or "PRAGMA" in upper_query else []
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
            elif "PRAGMA TABLE_INFO" in upper_query:
                columns = ["cid", "name", "type", "notnull", "dflt_value", "pk"]
            else:
                columns = []
            
            row_count = cursor.rowcount if not cursor.description and "PRAGMA" not in upper_query else len(rows)
            
            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": row_count if row_count != -1 else len(rows)
            }
        except Exception as e:
            if conn: conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            if conn: conn.close()

