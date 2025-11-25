"""
Entry point for FastAPI application
Run with: python main.py
Or with: uvicorn main:app --reload
"""

from src.api.main import app

if __name__ == "__main__":
    import uvicorn
    # Use import string for reload support when running with python main.py
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
