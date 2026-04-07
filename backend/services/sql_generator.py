from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import re

class SQLGeneratorService:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.llm = ChatOllama(
            model="mistral",
            temperature=0,
            base_url=ollama_url
        )
        
    def generate_sql(self, schema_context: str, user_query: str, is_admin: bool = False, db_path: str = "") -> str:
        role_name = "Superuser Database Controller" if is_admin else "Database Read-Only Assistant"
        
        examples = ""
        if is_admin:
            examples = """
### EXAMPLES:
User: "Add a new product named 'Laptop' with price 1200"
SQL: INSERT INTO products (name, unit_price) VALUES ('Laptop', 1200);

User: "Change price of item 5 to 100"
SQL: UPDATE products SET unit_price = 100 WHERE product_id = 5;

User: "Describe the products table"
SQL: PRAGMA table_info(products);

User: "Show me all tables"
SQL: SELECT name FROM sqlite_master WHERE type='table';
"""

        prompt = f"""### SYSTEM ROLE:
You are a {role_name} for an offline SQLite database.
Your task is to convert NL requests into valid, optimized SQLite.

### SCHEMA:
{schema_context}
{examples}
### CONSTRAINTS:
- Use EXACT table and column names from the schema above.
- Use 'LIKE %value%' for fuzzy string matching in WHERE clauses.
- Output ONLY the raw SQL query or PRAGMA statement. No markdown, no comments, no intro.
- If the user asks for all tables, use: SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';
- If the user asks for 'structure', 'describe', or 'columns', use: PRAGMA table_info(table_name);
- ONLY return 'NOT_SQL' if the request is social chatter.

### USER REQUEST:
"{user_query}"

### GENERTED SQL:"""
        
        response = self.llm.invoke(prompt)
        sql = response.content.strip()
        
        # Robust cleaning
        sql = re.sub(r'```(?:sql)?\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\s*```', '', sql)
        sql = sql.strip('`"\' ')
        
        # Final safety check for normal users
        if not is_admin:
            upper_sql = sql.upper()
            forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"]
            if any(f in upper_sql for f in forbidden):
                return "NOT_SQL"

        return sql.strip()

        
    def explain_query(self, sql: str, results_summary: str) -> str:
        """Provides a simple, non-technical explanation of the results or action."""
        prompt = f"""Summarize the outcome of this database action in one simple, professional sentence.
- If it was a search, state what was found.
- If it was a modification (Update/Insert/Delete), confirm that the change was applied to the requested records.
Avoid mentioning 'SQL', 'Rows', or technical jargon.

Action Summary: {results_summary}

Summary:"""
        response = self.llm.invoke(prompt)
        return response.content.strip()
