"""
API Middleware for CORS and error handling
"""
from flask import jsonify
from flask_cors import CORS
from datetime import datetime
import traceback

def setup_cors(app):
    """Setup CORS configuration"""
    CORS(app, origins=["http://localhost:5173", "http://localhost:3000"], supports_credentials=True)

def setup_error_handlers(app):
    """Setup global error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": str(error),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all uncaught exceptions"""
        error_details = {
            "error": str(error),
            "error_type": type(error).__name__,
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"❌ Unhandled exception: {error_details}")
        print(f"Traceback: {traceback.format_exc()}")
        
        return jsonify(error_details), 500
