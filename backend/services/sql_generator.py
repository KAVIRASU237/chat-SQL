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
        
        self.prompt_template = PromptTemplate(
            input_variables=["schema_context", "user_query"],
            template="""### ROLE: Expert SQLite Assistant
### TASK: Generate a valid SQL query based ON THE SCHEMA provided.

### SCHEMA:
{schema_context}

### RULES:
- If the user asks a general question (e.g., "hi", "hello", "who are you") or something NOT related to the database, return ONLY the word: "NOT_SQL".
- Use EXACT table and column names from the schema.
- Output ONLY the SQL query or "NOT_SQL".
- No explanations or markdown tags.
- Use JOIN if data from multiple tables is needed.

### USER QUESTION:
{user_query}

### SQL QUERY:"""
        )

    def generate_sql(self, schema_context: str, user_query: str) -> str:
        prompt = self.prompt_template.format(
            schema_context=schema_context,
            user_query=user_query
        )
        response = self.llm.invoke(prompt)
        sql = response.content.strip()
        
        # Clean markdown formatting
        sql = re.sub(r'```sql\n?', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'```\n?', '', sql)
        
        # Clean leading/trailing quotes and backticks
        sql = sql.strip('`"\' ')
        
        return sql.strip()
        
    def explain_query(self, sql: str, results_summary: str) -> str:
        """Provides a simple, non-technical explanation of the results."""
        prompt = f"""Summarize these database results in one or two very simple sentences for a non-technical user.
Avoid mentioning SQL, tables, or columns. Just state the final answer clearly.

Results Data: {results_summary}

Summary:"""
        response = self.llm.invoke(prompt)
        return response.content.strip()
