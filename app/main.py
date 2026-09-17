from fastapi import FastAPI

from app.db.database import engine

app = FastAPI(title="TABLETURN API", version="1.0.0")