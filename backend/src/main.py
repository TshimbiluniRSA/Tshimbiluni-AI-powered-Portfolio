import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from db.database import init_db, close_db
from routers import github, linkedin, chat, repositories, cv

# Configure logging
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

# FastAPI app
app = FastAPI(
    title="Tshimbiluni AI-powered Portfolio",
    description="Portfolio platform with AI-powered chat, GitHub/LinkedIn sync, and more.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(github.router)
app.include_router(linkedin.router)
app.include_router(chat.router)
app.include_router(repositories.router)
app.include_router(cv.router)

# Redirect root to docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# Startup event
@app.on_event("startup")
async def on_startup():
    logger.info("Starting Tshimbiluni AI-powered Portfolio app...")
    await init_db()
    logger.info("Database initialized.")

# Shutdown event
@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down Tshimbiluni AI-powered Portfolio app...")
    await close_db()
    logger.info("Database connections closed.")
