"""
Main Flask application entry point
"""
import os
from flask import Flask
from app.api.routes import api_bp
from app.api.middleware import setup_cors, setup_error_handlers

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Setup middleware
    setup_cors(app)
    setup_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    return app

def main():
    """Main entry point"""
    app = create_app()
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    print("🚀 Starting TikTok Compliance Analysis API...")
    print(f"📡 Port: {port}")
    print("📡 Available endpoints:")
    print("   GET  / - API information")
    print("   GET  /health - Health check")
    print("   POST /analyze - Analyze features")
    print("   GET  /analyze/sample - Sample analysis")
    print()
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
