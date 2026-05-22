from fastapi import FastAPI
from app.api.v1.router import api_router  # Import the API router
from app.core.config import settings  # Import application settings
from fastapi.middleware.cors import CORSMiddleware  # Middleware for handling CORS

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_PREFIX}/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

