import re

class SQLValidator:
    @staticmethod
    def is_safe(query: str) -> (bool, str):
        """
        Validates the SQL query for safety.
        Only SELECT statements are allowed.
        """
        # Clean leading/trailing junk that might bypass the generator's cleaning
        query_clean = query.strip('`"\' ').strip().lower()

        # Basic check: Must start with SELECT
        if not query_clean.startswith("select"):
            return False, f"Only SELECT queries are allowed for security reasons. (Received: {query[:20]}...)"

        # Block dangerous keywords
        forbidden_keywords = [
            "insert", "update", "delete", "drop", "truncate", 
            "alter", "create", "grant", "revoke", "exec", "execute"
        ]
        
        # Check if any forbidden keyword appears as a standalone word
        for word in forbidden_keywords:
            # Use regex to find whole words to avoid false positives (e.g. "updated_at")
            if re.search(r'\b' + re.escape(word) + r'\b', query_clean):
                return False, f"Forbidden operation detected: {word.upper()}"

        return True, "Query is safe."
