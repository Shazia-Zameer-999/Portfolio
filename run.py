"""
Development server entry point.
Run with: python run.py
"""
import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(
        port=int(os.environ.get("PORT", 9000)),
        debug=True,
    )
