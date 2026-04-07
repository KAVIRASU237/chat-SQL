from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from backend.core.config import settings
from backend.services.rag_service import RAGService
from backend.services.sql_generator import SQLGeneratorService
from backend.services.db_executor import DatabaseExecutor
from backend.services.graph_service import GraphGeneratorService
from backend.utils.sql_validator import SQLValidator
from backend.utils.schema_extractor import SchemaExtractor
from backend.services.dashboard_service import DashboardService
from backend.routers import admin
from backend.routers.admin import get_current_user

app = FastAPI(title=settings.PROJECT_NAME)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)

# Initialize services
rag_service = RAGService(settings.DATABASE_PATH, settings.VECTOR_STORE_PATH, settings.OLLAMA_URL)
sql_gen = SQLGeneratorService(settings.OLLAMA_URL)
db_executor = DatabaseExecutor(settings.DATABASE_PATH)
graph_gen = GraphGeneratorService()
dashboard_service = DashboardService(settings.OLLAMA_URL)
admin_service = admin.admin_service # Reuse the instance from router

class QueryRequest(BaseModel):
    question: str
    explain: bool = False
    generate_graph: bool = False

class DBConnectionRequest(BaseModel):
    db_path: str

@app.get("/status")
def get_status():
    db_exists = os.path.exists(settings.DATABASE_PATH)
    return {
        "status": "online",
        "database_connected": db_exists,
        "database_path": settings.DATABASE_PATH,
        "model": settings.LLM_MODEL
    }

@app.post("/connect")
def connect_db(req: DBConnectionRequest):
    if not os.path.exists(req.db_path):
        raise HTTPException(status_code=404, detail="Database file not found at the specified path.")
    
    settings.DATABASE_PATH = os.path.abspath(req.db_path)
    # Re-init services with new path
    global rag_service, db_executor
    rag_service = RAGService(settings.DATABASE_PATH, settings.VECTOR_STORE_PATH, settings.OLLAMA_URL)
    db_executor = DatabaseExecutor(settings.DATABASE_PATH)
    
    # Re-index schema
    num_docs = rag_service.index_schema()
    
    return {"message": f"Connected to {req.db_path}", "tables_indexed": num_docs}

@app.post("/ask")
def ask_question(req: QueryRequest, current_user: dict = Depends(get_current_user)):
    print(f"--- New Question: {req.question} ---")
    try:
        # 1. Retrieve Schema context
        schema_context = rag_service.retrieve_schema(req.question)
        print(f"Retrieved Schema Context: {schema_context[:200]}...")
        
        # 2. Generate SQL
        sql_query = sql_gen.generate_sql(schema_context, req.question, db_path=settings.DATABASE_PATH)
        print(f"Generated SQL: {sql_query}")
        
        if sql_query == "NOT_SQL":
            return {
                "sql": None,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "explanation": "Hello! I am your database assistant. Please ask me questions about your data (e.g., 'Show me all products').",
                "schema_used": None
            }

        if sql_query.startswith("ERROR"):
            print("SQL Generation Error detected.")
            return {"error": sql_query, "sql": None}

        # 3. Validate SQL
        is_safe, message = SQLValidator.is_safe(sql_query)
        if not is_safe:
            print(f"SQL Validation Failed: {message}")
            return {"error": message, "sql": sql_query}

        # 4. Execute SQL
        result = db_executor.execute_query(sql_query)
        
        if not result["success"]:
            print(f"SQL Execution Error: {result['error']}")
            return {"error": result["error"], "sql": sql_query}

        print(f"Execution Success! Rows returned: {result['row_count']}")

        explanation = None
        if req.explain:
            # Create a clear summary for the explanation service
            data_sample = result['rows'][:5] # Give a slightly larger sample
            summary = f"Total records found: {result['row_count']}. Data sample (first 5): {data_sample}. Header columns: {result['columns']}"
            explanation = sql_gen.explain_query(sql_query, summary)

        # 5. Generate Graph (if requested or inferred)
        graph_base64 = None
        # Simple intent detection: if query mentions "graph", "plot", "chart"
        intent_keywords = ["graph", "plot", "chart", "visualize"]
        user_wants_graph = req.generate_graph or any(k in req.question.lower() for k in intent_keywords)
        
        if user_wants_graph and result["rows"]:
            print("Generating graph...")
            try:
                # Provide columns and rows to the graph service
                # rows are list of tuples/lists, columns are list of strings
                graph_base64 = graph_gen.generate_graph(result["columns"], result["rows"])
                if graph_base64:
                    print("Graph generated successfully.")
                else:
                    print("Graph generation skipped (insufficient numeric data).")
            except Exception as e:
                print(f"Graph generation failed: {e}")

        response_data = {
            "sql": sql_query,
            "columns": result["columns"],
            "rows": result["rows"],
            "row_count": result["row_count"],
            "explanation": explanation,
            "graph_image": graph_base64,
            "schema_used": schema_context
        }

        # Save to history
        import json
        admin_service.save_chat(current_user["username"], req.question, json.dumps(response_data))

        return response_data

    except Exception as e:
        print(f"UNEXPECTED ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-dashboard")
def generate_dashboard(req: QueryRequest, current_user: dict = Depends(get_current_user)):
    """
    Generates a multi-component dashboard plan based on NL request.
    """
    try:
        # 1. Get Schema Context
        schema_context = rag_service.retrieve_schema(req.question)
        
        # 2. Generate Plan
        plan = dashboard_service.generate_dashboard_plan(schema_context, req.question)
        
        if "error" in plan:
            return plan

        # 3. Execute queries for each component to get real data
        for component in plan.get("components", []):
            sql = component["sql"]
            # Validate safety
            is_safe, _ = SQLValidator.is_safe(sql)
            if not is_safe:
                component["error"] = "Unsafe query generated."
                continue
                
            result = db_executor.execute_query(sql)
            if result["success"]:
                component["data"] = {
                    "columns": result["columns"],
                    "rows": result["rows"]
                }
                # Generate image for non-metric components
                if component["chart_type"] != "metric" and result["rows"]:
                    try:
                        img = graph_gen.generate_graph(result["columns"], result["rows"])
                        if img:
                            component["image"] = img
                    except Exception as e:
                        print(f"Component Graph Error: {e}")
            else:
                component["error"] = result["error"]

        return plan

    except Exception as e:
        print(f"DASHBOARD ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schema")
def get_full_schema():
    extractor = SchemaExtractor(settings.DATABASE_PATH)
    return {"schema": extractor.get_schema_docs()}

@app.get("/history")
def get_history(current_user: dict = Depends(get_current_user)):
    history = admin_service.get_chat_history(current_user["username"])
    return {"history": history}

@app.post("/history/clear")
def clear_history(current_user: dict = Depends(get_current_user)):
    admin_service.clear_chat_history(current_user["username"])
    return {"message": "History cleared"}

@app.delete("/history/{chat_id}")
def delete_chat(chat_id: int, current_user: dict = Depends(get_current_user)):
    admin_service.delete_chat_item(current_user["username"], chat_id)
    return {"message": "Chat deleted"}

# Serve Frontend
# Make sure the frontend folder exists and is visible to the backend
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/login")
def read_login():
    return FileResponse(os.path.join(frontend_path, "user_login.html"))

@app.get("/register")
def read_register():
    return FileResponse(os.path.join(frontend_path, "user_register.html"))

@app.get("/adminlogin")
def read_admin_login():
    return FileResponse(os.path.join(frontend_path, "admin_login.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
