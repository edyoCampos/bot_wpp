"""Debug test for message creation."""

import time

import requests

API_BASE = "http://localhost:3333/api/v1"
SIGNUP_URL = "http://localhost:3333/api/v1/auth/signup"
LOGIN_URL = "http://localhost:3333/api/v1/auth/login"


def test_message_creation():
    """Test basic message creation with detailed error info."""
    session = requests.Session()

    # 1. Create user
    timestamp = int(time.time() * 1000)
    email = f"debug_{timestamp}@example.com"
    password = "Test123!Secure"

    signup = requests.post(
        SIGNUP_URL, json={"email": email, "password": password, "full_name": "Debug User", "role": "admin"}, timeout=30
    )
    print(f"Signup: {signup.status_code} {signup.json()}")

    # 2. Login
    login = requests.post(LOGIN_URL, json={"email": email, "password": password}, timeout=30)
    print(f"Login: {login.status_code}")
    session.cookies.update(login.cookies)

    # 3. Create text message
    msg_response = requests.post(
        f"{API_BASE}/messages", json={"type": "text", "text": "Hello world"}, cookies=session.cookies, timeout=30
    )
    print(f"\nMessage creation: {msg_response.status_code}")
    print(f"Response: {msg_response.text}")


if __name__ == "__main__":
    test_message_creation()
