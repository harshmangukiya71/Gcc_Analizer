"""
Entry point wrapper for backwards compatibility with existing run scripts and terminal shortcuts.
Delegates to the modular backend application at backend.main:app.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.main import app

if __name__ == "__main__":
    import uvicorn
    print("=" * 65)
    print("GCC COMPASS: INDIA MARKET INSIGHTS DASHBOARD RUNNING")
    print("Open http://localhost:8000 in your browser")
    print("API Documentation available at http://localhost:8000/docs")
    print("=" * 65)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
