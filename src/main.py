from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.middlewares.rate_limit import limiter
from src.routes.index import api_router
from src.config.config import settings
from src.config.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    print("🚀 APP STARTING...")   # debug log
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# routes
app.include_router(api_router, prefix="/api")


# validation handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: object, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "message": "Validation failed"},
    )


# health check
@app.get("/health")
def health():
    return {"status": "ok"}


# root route (optional but useful)
@app.get("/")
def home():
    return {"status": "working 🚀"}