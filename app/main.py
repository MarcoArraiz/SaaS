from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from . import models, schemas, auth
from .database import engine, get_db
from .routers import products, orders
import os

app = FastAPI(title="Restaurant Management System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(products.router)
app.include_router(orders.router)

# Create tables
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Authentication endpoints
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Web routes
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.get("/admin")
async def admin_dashboard(
    request: Request,
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "user": current_user}
    )

@app.get("/user")
async def user_dashboard(
    request: Request,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return templates.TemplateResponse(
        "user/dashboard.html",
        {"request": request, "user": current_user}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
