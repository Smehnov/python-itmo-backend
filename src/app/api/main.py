from fastapi import FastAPI
from .routes import documents
from ..core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(documents.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Hello World"} 