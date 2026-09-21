from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.tables import router as tables_router

app = FastAPI(title="TABLETURN API", version="1.0.0")

app.include_router(auth_router)
app.include_router(tables_router)
