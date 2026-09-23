from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.tables import router as tables_router
from app.routes.reservations import router as reservations_router
from app.routes.menu import router as menu_router

app = FastAPI(title="TABLETURN API", version="1.0.0")

app.include_router(auth_router)
app.include_router(tables_router)
app.include_router(reservations_router)
app.include_router(menu_router)
