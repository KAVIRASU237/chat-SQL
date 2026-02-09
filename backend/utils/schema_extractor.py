import sqlite3
from typing import List, Dict

class SchemaExtractor:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_schema_docs(self) -> List[str]:
        """
        Extracts the schema from the SQLite database and converts it into
        natural language documents for embedding.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']

        schema_docs = []

        for table in tables:
            # Get column info
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            
            # Get foreign key info
            cursor.execute(f"PRAGMA foreign_key_list({table});")
            foreign_keys = cursor.fetchall()

            col_descriptions = []
            for col in columns:
                # col: (id, name, type, notnull, default_value, pk)
                pk_str = " (Primary Key)" if col[5] else ""
                col_descriptions.append(f"- {col[1]} ({col[2]}){pk_str}")

            fk_descriptions = []
            for fk in foreign_keys:
                # fk: (id, seq, table, from, to, on_update, on_delete, match)
                fk_descriptions.append(f"- Foreign Key: {fk[3]} references {fk[2]}({fk[4]})")

            doc = f"Table: {table}\n"
            doc += "Columns:\n" + "\n".join(col_descriptions) + "\n"
            if fk_descriptions:
                doc += "Relationships:\n" + "\n".join(fk_descriptions) + "\n"
            
            schema_docs.append(doc)

        conn.close()
        return schema_docs

    def get_table_names(self) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
        conn.close()
        return tables
