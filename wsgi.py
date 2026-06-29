"""
Production WSGI entry point.
Deploy with: gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 2 --timeout 120

With Nginx in front, use Unix socket:
gunicorn wsgi:app --bind unix:/tmp/portfolio.sock --workers 2
"""
import os
from app import create_app

app = create_app("production")
