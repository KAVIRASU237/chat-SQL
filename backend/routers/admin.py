from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from backend.services.auth_service import AuthService, Token
from backend.services.db_executor import DatabaseExecutor
from backend.services.rag_service import RAGService
from backend.services.sql_generator import SQLGeneratorService
from backend.core.config import settings

from backend.services.admin_service import AdminService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Initialize Services
admin_service = AdminService()
db_executor = DatabaseExecutor(settings.DATABASE_PATH)
rag_service = RAGService(settings.DATABASE_PATH, settings.VECTOR_STORE_PATH, settings.OLLAMA_URL)
sql_gen = SQLGeneratorService(settings.OLLAMA_URL)

class QueryRequest(BaseModel):
    question: str
    explain: bool = False

class SQLRequest(BaseModel):
    query: str

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = AuthService.verify_token(token, credentials_exception)
    user = admin_service.get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = admin_service.get_user(form_data.username)
    if not user or not AuthService.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = AuthService.create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/admin/execute")
async def execute_admin_sql(req: SQLRequest, current_user: dict = Depends(get_current_admin)):
    """
    Executes raw SQL without safety checks (Admin only).
    Allows INSERT, UPDATE, DELETE, etc.
    """
    admin_service.log_action(current_user['username'], "RAW_SQL_EXECUTION", req.query)
    result = db_executor.execute_query(req.query)
    
    if not result["success"]:
        return {"error": result["error"], "sql": req.query}
        
    return result

@router.post("/admin/ask")
async def ask_admin_question(req: QueryRequest, current_user: dict = Depends(get_current_admin)):
    """
    NLP for Admin with CRUD capabilities.
    """
    try:
        # 1. Retrieve Schema context
        schema_context = rag_service.retrieve_schema(req.question)
        
        # 2. Generate SQL (is_admin=True allows CRUD)
        sql_query = sql_gen.generate_sql(schema_context, req.question, is_admin=True)
        
        if sql_query == "NOT_SQL":
            return {"error": "Irrelevant question. Please ask something related to the database.", "sql": None}

        # 3. Log Action
        admin_service.log_action(current_user['username'], "NLP_ACTION", sql_query)
        
        # 4. Execute SQL
        result = db_executor.execute_query(sql_query)
        
        explanation = None
        if req.explain and result.get("success"):
            # Provide better context for AI Insight
            if result.get("rows"):
                summary = f"The query returned {result['row_count']} results. Sample: {str(result['rows'][:5])}"
            else:
                summary = f"The modification was successful. {result['row_count']} rows were affected."
            
            explanation = sql_gen.explain_query(sql_query, summary)

        return {
            "sql": sql_query,
            "columns": result.get("columns", []),
            "rows": result.get("rows", []),
            "row_count": result.get("row_count", 0),
            "explanation": explanation,
            "success": result.get("success"),
            "error": result.get("error") if not result.get("success") else None
        }

    except Exception as e:
        print(f"ADMIN NLP ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


