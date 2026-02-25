"""
EQUINOX Flood Watch - WSGI Entry Point
Production WSGI configuration
"""

import os
import sys

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from app import app

if __name__ == "__main__":
    app.run()
// 2026-01-10 09:44:42 UI component update

# 2026-02-25 10:52:30 weather data integration
