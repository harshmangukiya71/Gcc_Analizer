import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.api.routes import router as api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Professional enterprise analytics for Indian Global Capability Centers (GCCs)",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware (permits local dev servers, extensions, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for CSS, JS, Assets
if settings.FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(settings.FRONTEND_DIR)), name="static")

# Include Modular API Routers
app.include_router(api_router)

# Serve Frontend SPA / Dashboard
@app.get("/", summary="Dashboard User Interface")
def serve_index():
    index_file = settings.FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend not found. Please verify frontend/index.html exists."}


if __name__ == "__main__":
    import uvicorn
    print("=" * 65)
    print("GCC COMPASS: INDIA MARKET INSIGHTS DASHBOARD RUNNING")
    print("Open http://localhost:8000 in your browser")
    print("API Documentation available at http://localhost:8000/docs")
    print("=" * 65)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
