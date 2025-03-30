import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from .database import create_db_and_tables
from .routers import users


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle the startup and shutdown of the application."""
    logger.info("Starting the application")
    create_db_and_tables()
    yield
    logger.info("Shutting down the application")


app = FastAPI(title="Mocked User Service", lifespan=lifespan)

# Include the users router
app.include_router(users.router)


# Root endpoint
@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "The Mocked User Service API is running"}
