from langchain_ollama import ChatOllama
import json
import re

class DashboardService:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.llm = ChatOllama(
            model="mistral",
            temperature=0,
            base_url=ollama_url
        )

    def generate_dashboard_plan(self, schema_context: str, user_request: str) -> dict:
        """
        Converts a natural language request into a multi-component dashboard plan.
        """
        prompt = f"""### SYSTEM ROLE:
You are an expert Data Analyst for an offline SQLite database.
Your task is to convert a natural language analytics request into a structured dashboard plan.

### SCHEMA:
{schema_context}

### INSTRUCTIONS:
1. Break the user request into exactly 3-4 distinct analytical components.
2. Generate optimized SQL queries for each component.
3. Select the correct chart type automatically:
   - Time-based trend → LINE chart
   - Category comparison → BAR chart
   - Distribution / proportion → PIE chart
   - Single KPI → METRIC card
4. Ensure all SQL is valid SQLite syntax.
5. Only generate SELECT queries.
6. Use clear column aliases for visualization (e.g., total_sales, category).

### OUTPUT FORMAT (JSON ONLY):
{{
  "dashboard_title": "...",
  "components": [
    {{
      "title": "...",
      "description": "...",
      "chart_type": "line | bar | pie | metric",
      "sql": "SELECT ...",
      "x_axis": "column_name",
      "y_axis": "column_name"
    }}
  ]
}}

### USER REQUEST:
"{user_request}"

### JSON PLAN:"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Extract JSON from potential markdown markers
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            return json.loads(content)
        except Exception as e:
            return {"error": f"Failed to generate dashboard plan: {str(e)}"}
