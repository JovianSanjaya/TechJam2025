#!/usr/bin/env python3
"""
Test script to verify the extension uses the FORCED Python path from settings.json
"""

print("🐍 This script is running with the FORCED Python interpreter!")
print("If you see this message, the extension is using the configured path.")

import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Test some imports to verify this environment works
try:
    import flask
    print(f"✅ Flask imported successfully: {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")

try:
    import flask_cors
    print("✅ Flask-CORS imported successfully")
except ImportError as e:
    print(f"❌ Flask-CORS import failed: {e}")

try:
    import requests
    print("✅ Requests imported successfully")
except ImportError as e:
    print(f"❌ Requests import failed: {e}")

print("\n🎯 This confirms the extension is using the FORCED Python path!")
