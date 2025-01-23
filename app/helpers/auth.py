"""
Authentication helper functions handling authentication using
OpenID Connect and JWT through the authlib library.
"""

from authlib.integrations.flask_client import OAuth
import os

oauth = OAuth()

def init_oauth(app):
    """
    Initializes OAuth with OpenID Connect.
    """
    oauth.init_app(app)
    oauth.register(
        'google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        client_kwargs={'scope': 'openid email profile'}
    )
