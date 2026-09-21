from typing import Annotated

from fastapi import Depends, FastAPI

from app.core.deps import get_current_user
from app.models.user import User
from app.routes.auth import router as auth_router


app = FastAPI(
    title="TABLETURN API",
    version="1.0.0",
)

app.include_router(auth_router)


@app.get("/test-auth")
def test_auth(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return {
        "message": "Authentication works",
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }