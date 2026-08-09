from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from routes.auth import router as auth_router
from routes.admin_auth import router as admin_router
from routes.product import router as product_router
from routes.admin_product import router as admin_product_router
from routes.cart import router as cart_router
from routes.home import router as home_router
from routes.contact import router as contact_router

from utils.database import Base, engine
from models.user import User
from models.address import Address


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Kisan Breed API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:56823",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTES
# =========================================================

app.include_router(auth_router)

app.include_router(admin_router)

app.include_router(product_router)

app.include_router(admin_product_router)

app.include_router(cart_router)

app.include_router(home_router)

app.include_router(contact_router)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/attachments",
    StaticFiles(directory="attachments"),
    name="attachments"
)


# =========================================================
# HEALTH
# =========================================================

@app.get("/")
def home():

    return {
        "status": "success",
        "message": "Kisan Breed Backend Running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )