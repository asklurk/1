import os
from flask import Flask, redirect, url_for, session, render_template, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "test-secret-123")

# OAuth configuration
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.route('/')
def home():
    if 'user' in session:
        user_info = session['user']
        return f"""
        <h1>Welcome {user_info['name']}!</h1>
        <p>Email: {user_info['email']}</p>
        <p>Google ID: {user_info['google_id']}</p>
        <a href="/logout">Logout</a>
        <br><br>
        <a href="/test-data">Test JSON Data</a>
        """
    return '''
    <h1>Google OAuth Test</h1>
    <a href="/login">Login with Google</a>
    <br><br>
    <a href="/test-data">Test JSON Data</a>
    '''

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        if user_info:
            session['user'] = {
                'name': user_info['name'],
                'email': user_info['email'],
                'google_id': user_info['sub']
            }
        return redirect('/')
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/test-data')
def test_data():
    return jsonify({
        "status": "success",
        "user_authenticated": 'user' in session,
        "google_configured": bool(os.environ.get("GOOGLE_CLIENT_ID")),
        "message": "API is working!"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
