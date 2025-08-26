import os
from dotenv import load_dotenv
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional, Dict, Any
from config.database import SessionLocal
from models.database_models import User
from datetime import datetime
from urllib.parse import urlparse
from psycopg2 import OperationalError
import json

load_dotenv()

# Initialize Firebase Admin SDK (if not already initialized)
if not firebase_admin._apps:
    firebase_json_str = os.environ.get("FIREBASE_JSON")
    firebase_service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    if firebase_json_str:
        cred_dict = json.loads(firebase_json_str)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    elif firebase_service_account_path and os.path.exists(firebase_service_account_path):
        cred = credentials.Certificate(firebase_service_account_path)
        firebase_admin.initialize_app(cred)
    else:
        st.error(
            "Firebase credentials not found. Please set FIREBASE_JSON or provide firebase-service-account.json.")
        st.stop()


def get_or_create_db_user(uid: str, email: str, full_name: str):
    """Get or create a user in the database based on Firebase UID."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            print(
                f"DEBUG: User with UID {uid} not found. Creating new user...")
            user = User(
                id=uid,
                email=email,
                full_name=full_name,
                created_at=datetime.utcnow(),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"DEBUG: New user created with ID: {user.id}")
        else:
            print(f"DEBUG: User with UID {uid} found in DB.")
        return user
    except OperationalError as oe:
        db.rollback()
        st.error(
            "Database connection failed. Please try again later or contact support.")
        print(
            f"ERROR: Database connection failed in get_or_create_db_user: {oe}")
        return None
    except Exception as e:
        db.rollback()  # Rollback on error
        print(
            f"ERROR: Database operation failed in get_or_create_db_user: {e}")
        raise  # Re-raise the exception after logging
    finally:
        db.close()


def get_current_firebase_user() -> Optional[Dict[str, Any]]:
    """Gets the current authenticated Firebase user from session state or URL token."""
    # Check for Firebase token in URL parameters
    query_params = st.query_params
    firebase_token = query_params.get("firebase_token", None)

    if firebase_token:
        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(firebase_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            name = decoded_token.get('name', email.split(
                '@')[0] if email else 'Unknown User')

            # Get or create user in our PostgreSQL database
            db_user = get_or_create_db_user(uid, email, name)
            if db_user is None:
                st.warning(
                    "Unable to log you in due to a database connection issue. Please try again later.")
                return None

            # Store actual user data in session state
            st.session_state.user = {
                "id": db_user.id,
                "email": db_user.email,
                "full_name": db_user.full_name,
                "is_active": db_user.is_active
            }
            # Clear the token from the URL to prevent re-processing on refresh
            st.query_params.clear()

        except Exception as e:
            st.error(f"Firebase token verification failed: {e}")
            if "user" in st.session_state:
                del st.session_state.user  # Clear partial session
            return None

    if "user" not in st.session_state:
        return None
    return st.session_state.user


def logout_user():
    """Logs out the current user by clearing session state."""
    if "user" in st.session_state:
        del st.session_state.user
    # st.rerun() # Removed as it's a no-op within a callback and not strictly needed here


def login_required(func):
    """Decorator to require login for Streamlit pages/sections."""
    def wrapper(*args, **kwargs):
        if not get_current_firebase_user():
            st.warning("Please log in to access this feature.")
            login_url = get_login_url()
            st.markdown(f"""
            <a href="{login_url}" target="_self">
                <button style="padding: 10px 20px; background-color: #16610E; color: #C7E8FF; font-weight: 400; border: none; border-radius: 5px; cursor: pointer;">
                    Sign In with Google
                </button>
            </a>
            """, unsafe_allow_html=True)
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def get_login_url():
    """Get the login URL based on environment"""

    # 1. Development: use local static server
    if os.getenv("ENVIRONMENT", "").lower() == "development":
        return "http://localhost:8000/login.html"

    # 2. Production: use static site if available
    # e.g. https://jurist-ai-static.onrender.com
    static_url = os.getenv("STATIC_LOGIN_URL")
    if static_url:
        return f"{static_url}/login.html"

    # 3. Render fallback
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        return f"{render_url.replace('http://', 'https://')}/login.html"

    # 4. Otherwise, use the current domain
    query_params_dict = st.query_params
    current_url_list = query_params_dict.get("_stcore", [""])
    current_url = current_url_list[0] if current_url_list else ""
    if current_url:
        parsed_url = urlparse(current_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return f"{base_url}/login.html"

    # 5. Last fallback
    return "/login.html"


# import os
# from dotenv import load_dotenv
# import streamlit as st
# import firebase_admin
# from firebase_admin import credentials, auth
# from typing import Optional, Dict, Any
# from config.database import SessionLocal
# from models.database_models import User
# from datetime import datetime
# from psycopg2 import OperationalError

# load_dotenv()

# # Initialize Firebase Admin SDK (if not already initialized)
# if not firebase_admin._apps:
#     # Assuming your service account key is in .env or as a file
#     # For local development, you might store it as a JSON file and reference its path
#     # For deployment, consider Firebase environment variables or other secure methods
#     # For now, let's assume the path to your service account key is in an environment variable
#     firebase_service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
#     if firebase_service_account_path and os.path.exists(firebase_service_account_path):
#         cred = credentials.Certificate(firebase_service_account_path)
#         firebase_admin.initialize_app(cred)
#     else:
#         st.error("Firebase service account path not found or invalid.")
#         st.stop()

# def get_or_create_db_user(uid: str, email: str, full_name: str):
#     """Get or create a user in the database based on Firebase UID."""
#     db = SessionLocal()
#     try:
#         user = db.query(User).filter(User.id == uid).first()
#         if not user:
#             print(f"DEBUG: User with UID {uid} not found. Creating new user...")
#             user = User(
#                 id=uid,
#                 email=email,
#                 full_name=full_name,
#                 created_at=datetime.utcnow(),
#                 is_active=True
#             )
#             db.add(user)
#             db.commit()
#             db.refresh(user)
#             print(f"DEBUG: New user created with ID: {user.id}")
#         else:
#             print(f"DEBUG: User with UID {uid} found in DB.")
#         return user
#     except OperationalError as oe:
#         db.rollback()
#         st.error("Database connection failed. Please try again later or contact support.")
#         print(f"ERROR: Database connection failed in get_or_create_db_user: {oe}")
#         return None
#     except Exception as e:
#         db.rollback() # Rollback on error
#         print(f"ERROR: Database operation failed in get_or_create_db_user: {e}")
#         raise # Re-raise the exception after logging
#     finally:
#         db.close()

# def get_current_firebase_user() -> Optional[Dict[str, Any]]:
#     """Gets the current authenticated Firebase user from session state or URL token."""
#     # Check for Firebase token in URL parameters
#     query_params = st.query_params
#     firebase_token = query_params.get("firebase_token", None)

#     if firebase_token:
#         try:
#             # Verify the Firebase ID token
#             decoded_token = auth.verify_id_token(firebase_token)
#             uid = decoded_token['uid']
#             email = decoded_token.get('email')
#             name = decoded_token.get('name', email.split('@')[0] if email else 'Unknown User')

#             # Get or create user in our PostgreSQL database
#             db_user = get_or_create_db_user(uid, email, name)
#             if db_user is None:
#                 st.warning("Unable to log you in due to a database connection issue. Please try again later.")
#                 return None

#             # Store actual user data in session state
#             st.session_state.user = {
#                 "id": db_user.id,
#                 "email": db_user.email,
#                 "full_name": db_user.full_name,
#                 "is_active": db_user.is_active
#             }
#             # Clear the token from the URL to prevent re-processing on refresh
#             st.query_params.clear()

#         except Exception as e:
#             st.error(f"Firebase token verification failed: {e}")
#             if "user" in st.session_state: del st.session_state.user # Clear partial session
#             return None

#     if "user" not in st.session_state:
#         return None
#     return st.session_state.user

# def logout_user():
#     """Logs out the current user by clearing session state."""
#     if "user" in st.session_state:
#         del st.session_state.user
#     st.rerun()

# def login_required(func):
#     """Decorator to require login for Streamlit pages/sections."""
#     def wrapper(*args, **kwargs):
#         if not get_current_firebase_user():
#             st.warning("Please log in to access this feature.")
#             st.markdown("""
#             <a href="http://localhost:8000/login.html" target="_self">
#                 <button style="padding: 10px 20px; background-color: #16610E; color: #C7E8FF; font-weight: 400; border: none; border-radius: 5px; cursor: pointer;">
#                     Sign In with Google
#                 </button>
#             </a>
#             """, unsafe_allow_html=True)
#             st.stop()
#         return func(*args, **kwargs)
#     return wrapper
