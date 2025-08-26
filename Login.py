import streamlit as st
import pyrebase
import json
import requests

# --- Firebase Config from your Firebase Console ---
firebase_config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_PROJECT.firebaseapp.com",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_PROJECT.appspot.com",
    "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
    "appId": "YOUR_APP_ID"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

st.set_page_config(page_title="Legal AI Login", page_icon="🧑‍⚖️")

st.title("🔐 Login to Use Legal AI")

# Google OAuth Login Button
login_url = (
    f"https://accounts.google.com/o/oauth2/v2/auth"
    f"?client_id=YOUR_GOOGLE_CLIENT_ID"
    f"&redirect_uri=http://localhost:8501"
    f"&response_type=token"
    f"&scope=email"
)

st.markdown(f"[Login with Google]({login_url})")

# Capture OAuth Token from URL (after login redirect)
query_params = st.experimental_get_query_params()

if "access_token" in query_params:
    access_token = query_params["access_token"][0]

    # Verify token with Google API
    user_info_url = f"https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={access_token}"
    res = requests.get(user_info_url)
    
    if res.status_code == 200:
        user_data = res.json()
        email = user_data.get("email")
        st.success(f"✅ Logged in as {email}")
        
        # Save to session or use in app
        st.session_state["user_email"] = email
    else:
        st.error("⚠️ Failed to retrieve user info.")

elif "user_email" in st.session_state:
    st.success(f"✅ Welcome back {st.session_state['user_email']}")

else:
    st.warning("Please log in to continue.")

