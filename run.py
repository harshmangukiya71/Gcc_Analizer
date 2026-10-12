#!/usr/bin/env python3
"""
GCC Analyzer Application Launcher
---------------------------------
Run this script to start the full-stack GCC Compass application:
    python run.py
"""
import sys
from pathlib import Path

# Ensure project root is in Python module search path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 65)
    print("🚀 GCC COMPASS - INDIA MARKET INSIGHTS DASHBOARD")
    print("=" * 65)
    print("🌐 Dashboard UI:     http://localhost:8000")
    print("📚 API Docs:         http://localhost:8000/docs")
    print("🔧 OpenAPI Schema:   http://localhost:8000/openapi.json")
    print("=" * 65 + "\n")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
