import os
import json
import logging
from flask import Flask, request, Response, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-123")
CORS(app)

# Simple token estimation
def estimate_tokens(text):
    """Simple token estimation - roughly 4 characters per token"""
    if not text:
        return 0
    return len(text) // 4

TOKEN_LIMIT = 300_000
tokens_used = 0
KEY = os.getenv("OPENROUTER_API_KEY")

# Authentication routes
@app.route('/')
def home():
    """Main route - redirects to login if not authenticated"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', KEY=KEY)

@app.route('/login')
def login():
    """Login page"""
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('google.html')

@app.route('/login/google')
def google_login():
    """Initiate Google OAuth flow"""
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    if not client_id:
        return "Google OAuth not configured. Please add GOOGLE_CLIENT_ID to environment variables.", 500
    
    # For now, simulate login since OAuth might be complex initially
    session['user'] = {
        'name': 'Test User',
        'email': 'test@example.com', 
        'google_id': 'test123'
    }
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    return redirect(url_for('login'))

# Basic routes for testing
@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "api_key_configured": bool(KEY),
        "tokens_used": tokens_used,
        "environment": "production"
    })

@app.route("/test")
def test():
    """Test route"""
    return jsonify({
        "status": "success", 
        "message": "Pentad Chat API is working!",
        "ai_configured": bool(KEY),
        "user_authenticated": 'user' in session
    })

@app.route("/tokens", methods=["GET"])
def get_tokens():
    """Endpoint to get current token usage"""
    return jsonify({
        "tokens_used": tokens_used,
        "token_limit": TOKEN_LIMIT,
        "remaining_tokens": TOKEN_LIMIT - tokens_used,
        "usage_percentage": (tokens_used / TOKEN_LIMIT) * 100
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Vercel compatibility
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("🚀 Starting Pentad Chat Server...")
    print(f"📍 Local: http://localhost:{port}")
    print(f"🔧 Debug: {debug}")
    print(f"🤖 AI: {'✅ Enabled' if KEY else '❌ Disabled'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
else:
    # For Vercel serverless
    application = app
