import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import db, create_document, get_documents
from schemas import MenuItem, ChatMessage

app = FastAPI(title="District 2nd - Public Service & Cafe API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"service": "District 2nd API", "status": "ok"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Schemas endpoint for viewer
@app.get("/schema")
def get_schema():
    return {
        "menuitem": {
            "name": "string",
            "description": "string | null",
            "price": 0,
            "category": "string",
            "image_url": "url",
            "tags": ["string"]
        },
        "chatmessage": {
            "session_id": "string",
            "role": "user|assistant",
            "text": "string",
            "language": "string | null"
        }
    }

# Menu Endpoints
@app.post("/api/menu", response_model=dict)
def add_menu_item(item: MenuItem):
    try:
        inserted_id = create_document("menuitem", item)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu", response_model=List[dict])
def list_menu_items(q: Optional[str] = Query(None), category: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=200)):
    try:
        filter_query = {}
        if category:
            filter_query["category"] = category
        items = get_documents("menuitem", filter_query, limit)
        # basic predictive search scoring
        if q:
            text = q.lower()
            def score(it):
                s = 0
                if text in it.get("name", "").lower(): s += 3
                if text in (it.get("description") or "").lower(): s += 2
                if any(text in t.lower() for t in it.get("tags", [])): s += 2
                return s
            items.sort(key=score, reverse=True)
        # map ObjectId to str for _id
        for it in items:
            if "_id" in it:
                it["id"] = str(it.pop("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat Endpoints (store messages; frontend will call external LLM if provided)
class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: Optional[str] = None

@app.post("/api/chat")
def store_chat(req: ChatRequest):
    try:
        create_document("chatmessage", ChatMessage(session_id=req.session_id, role="user", text=req.message, language=req.language))
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
