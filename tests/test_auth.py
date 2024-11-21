"""
Tests for authentication functionality.
"""

def test_login_oidc(client):
    """
    Test OpenID Connect login.
    """
    # Mock the OIDC process 
    response = client.get("/api/login")
    assert response.status_code == 302  # Redirect to Google
