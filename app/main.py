from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.tables import router as tables_router
from app.routes.reservations import router as reservations_router
from app.routes.menu import router as menu_router
from app.routes.orders import router as orders_router
from app.routes.kitchen import router as kitchen_router
from app.routes.webhook import router as webhook_router
from app.routes.reports import router as reports_router


app = FastAPI(
    title="TABLETURN API",
    version="1.0.0",
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(tables_router, prefix="/api/v1")
app.include_router(reservations_router, prefix="/api/v1")
app.include_router(menu_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(kitchen_router, prefix="/api/v1")
app.include_router(webhook_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")