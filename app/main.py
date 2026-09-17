from fastapi import FastAPI

from app.db.database import engine

app = FastAPI(title="TABLETURN API", version="1.0.0")


@app.get("/")
async def home():
    return {"status": "healthy", "message": "TableTurn API is online!"}