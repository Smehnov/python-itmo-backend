from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest, make_asgi_app
from .api.routes import documents
from .core.database import init_db
from .core.config import settings
from .core.metrics import APP_INFO, REQUEST_COUNT, REQUEST_DURATION
from starlette.middleware.base import BaseHTTPMiddleware
import time

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(time.time() - start_time)
        return response

app.add_middleware(MetricsMiddleware)

# Add prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Endpoint to expose Prometheus metrics"""
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )

# Set application info
APP_INFO.info({
    'version': '1.0.0',
    'environment': getattr(settings, 'ENVIRONMENT', 'development')
})

# Initialize database
init_db()

# Include routers
app.include_router(
    documents.router,
    prefix=settings.API_V1_STR,
    tags=["documents"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 