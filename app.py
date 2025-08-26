# === FILE: app.py ===
import streamlit as st
from modules.chat_assistant import chat_interface
from modules.document_reviewer import document_review_ui
from modules.legal_template import template_builder_ui
from modules.law_search import law_search_ui
from modules.query_builder import query_builder_ui
from utils.auth import get_current_firebase_user, logout_user
from utils.db_utils import get_user_chat_sessions
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

# -------------------- LOAD ENV + INIT FIREBASE --------------------
load_dotenv()

firebase_json_str = os.environ.get("FIREBASE_JSON")
firebase_key_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json")

if not firebase_admin._apps:
    if firebase_json_str:
        # Running from JSON in env var (Render)
        import json
        cred_dict = json.loads(firebase_json_str)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    elif os.path.exists(firebase_key_path):
        # Running locally from file
        cred = credentials.Certificate(firebase_key_path)
        firebase_admin.initialize_app(cred)
    else:
        st.error("❌ Firebase credentials not found. Please set FIREBASE_JSON or provide firebase-service-account.json.")
        st.stop()


# -------------------- CONFIG --------------------
st.set_page_config(page_title="JuristAI - Naija Legal AI Assistant", page_icon="💎", layout="wide")
st.title("JuristAI - Naija's no. 1 Legal AI Platform")

# -------------------- AUTH --------------------
user = get_current_firebase_user()
if user:
    st.sidebar.success(f"Welcome {user['full_name']}!")
    st.sidebar.button("Logout", on_click=logout_user)
else:
    st.sidebar.info("Sign in to access all features.")

# -------------------- SIDEBAR --------------------
st.sidebar.title("⚖️ Features")
selection = st.sidebar.radio("Select a tool:", [
    "📜 Document Review",
    "💬 AI Chat Assistant",
    "📝 Legal Template Builder",
    "🔍 Legal Law Search",
    "📂 AI Query Panel"
])

# --- Chat History for Assistant ---
if selection == "💬 AI Chat Assistant" and user:
    from config.database import SessionLocal

    if "chat_sessions" not in st.session_state:
        with SessionLocal() as db:
            st.session_state.chat_sessions = get_user_chat_sessions(db, user['id'])
        st.session_state.current_chat = (
            st.session_state.chat_sessions[0]["session_id"] if st.session_state.chat_sessions else None
        )

    st.sidebar.markdown("---")
    st.sidebar.subheader("🧠 Chat Sessions")

    if st.sidebar.button("➕ New Chat"):
        import time
        new_id = f"chat_{int(time.time())}"
        new_title = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions.append({
            "session_id": new_id,
            "title": new_title,
            "created_at": None
        })
        st.session_state.current_chat = new_id
        st.experimental_rerun()

    for session in st.session_state.chat_sessions:
        sid = session["session_id"]
        title = session["title"]

        if st.sidebar.button(title, key=sid, use_container_width=True):
            st.session_state.current_chat = sid
            st.experimental_rerun()

        if sid == st.session_state.current_chat:
            if st.sidebar.button(f"❌ Delete {title}", key=f"del_{sid}"):
                st.session_state.chat_sessions = [
                    s for s in st.session_state.chat_sessions if s["session_id"] != sid
                ]
                st.session_state.current_chat = (
                    st.session_state.chat_sessions[0]["session_id"]
                    if st.session_state.chat_sessions else None
                )
                st.experimental_rerun()

# -------------------- TOOL ROUTER --------------------
if selection == "📜 Document Review":
    document_review_ui()
elif selection == "💬 AI Chat Assistant":
    chat_interface()
elif selection == "📝 Legal Template Builder":
    template_builder_ui()
elif selection == "🔍 Legal Law Search":
    law_search_ui()
elif selection == "📂 AI Query Panel":
    query_builder_ui()

# -------------------- SIDEBAR FOOTER --------------------
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div class="sidebar-footer">
    <p style="font-size: 19px; text-align: center; color: #47D1FD;"><em>Beta Release</em></p>
    <hr style="margin-top: 0; margin-bottom: 2px;">
    <p style="font-size: 15px; text-align: center;">
        © <a href="https://www.techxos.com" target="_blank" style="text-decoration: none; color: white;">
        Techxos Digital Solutions 2025</a>
    </p>
    <p style="font-size: 17px; text-align: center; margin-bottom: 16px;">
        <a href="https://www.techxos.com" target="_blank" style="text-decoration: none; color: white;">
        www.techxos.com</a>
    </p>
</div>
""", unsafe_allow_html=True)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
    [data-testid="collapsedControl"] {
        transform: scale(1.5);
        margin-top: 10px;
        margin-left: 8px;
    }
    [data-testid="stTextInput"] {
        margin-top: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)





# # === FILE: app.py ===
# import streamlit as st
# from modules.chat_assistant import chat_interface
# from modules.document_reviewer import document_review_ui
# from modules.legal_template import template_builder_ui
# from modules.law_search import law_search_ui
# from modules.query_builder import query_builder_ui
# from utils.auth import get_current_firebase_user, login_required, logout_user
# from utils.db_utils import get_user_chat_sessions
# import os
# from dotenv import load_dotenv
# import firebase_admin
# from firebase_admin import credentials

# # -------------------- LOAD ENV + INIT FIREBASE --------------------
# load_dotenv()
# firebase_key_path = "firebase-service-account.json"

# if not firebase_admin._apps:
#     if os.path.exists(firebase_key_path):
#         cred = credentials.Certificate(firebase_key_path)
#         firebase_admin.initialize_app(cred)
#     else:
#         st.error("❌ Firebase credentials file not found. Please add 'firebase-service-account.json'.")
#         st.stop()

# # -------------------- CONFIG --------------------
# st.set_page_config(page_title="JuristAI - Naija Legal AI Assistant", page_icon="💎", layout="wide")
# st.title("JuristAI - Naija's no. 1 Legal AI Platform")

# # -------------------- AUTH --------------------
# user = get_current_firebase_user()
# if user:
#     st.sidebar.success(f"Welcome {user['full_name']}!")
#     st.sidebar.button("Logout", on_click=logout_user)
# else:
#     st.sidebar.info("Sign in to access all features.")

# # -------------------- SIDEBAR --------------------
# st.sidebar.title("⚖️ Features")
# selection = st.sidebar.radio("Select a tool:", [
#     "📜 Document Review",
#     "💬 AI Chat Assistant",
#     "📝 Legal Template Builder",
#     "🔍 Legal Law Search",
#     "📂 AI Query Panel"
# ])

# # --- Chat History for Assistant ---
# if selection == "💬 AI Chat Assistant" and user:
#     from config.database import SessionLocal

#     if "chat_sessions" not in st.session_state:
#         with SessionLocal() as db:
#             st.session_state.chat_sessions = get_user_chat_sessions(db, user['id'])
#         st.session_state.chat_sessions = [
#             {"session_id": s.session_id, "title": s.title} for s in st.session_state.chat_sessions
#         ]
#         st.session_state.current_chat = (
#             st.session_state.chat_sessions[0]["session_id"] if st.session_state.chat_sessions else None
#         )

#     st.sidebar.markdown("---")
#     st.sidebar.subheader("🧠 Chat Sessions")

#     if st.sidebar.button("➕ New Chat"):
#         import time
#         new_id = f"chat_{int(time.time())}"
#         new_title = f"Chat {len(st.session_state.chat_sessions) + 1}"
#         st.session_state.chat_sessions.append({
#             "session_id": new_id,
#             "title": new_title
#         })
#         st.session_state.current_chat = new_id
#         st.experimental_rerun()

#     for session in st.session_state.chat_sessions:
#         sid = session["session_id"]
#         title = session["title"]

#         if st.sidebar.button(title, key=sid, use_container_width=True):
#             st.session_state.current_chat = sid
#             st.experimental_rerun()

#         if sid == st.session_state.current_chat:
#             if st.sidebar.button(f"❌ Delete {title}", key=f"del_{sid}"):
#                 st.session_state.chat_sessions = [
#                     s for s in st.session_state.chat_sessions if s["session_id"] != sid
#                 ]
#                 st.session_state.current_chat = (
#                     st.session_state.chat_sessions[0]["session_id"]
#                     if st.session_state.chat_sessions else None
#                 )
#                 st.experimental_rerun()

# # -------------------- TOOL ROUTER --------------------
# if selection == "📜 Document Review":
#     document_review_ui()
# elif selection == "💬 AI Chat Assistant":
#     chat_interface()
# elif selection == "📝 Legal Template Builder":
#     template_builder_ui()
# elif selection == "🔍 Legal Law Search":
#     law_search_ui()
# elif selection == "📂 AI Query Panel":
#     query_builder_ui()

# # -------------------- SIDEBAR FOOTER --------------------
# st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
# st.sidebar.markdown("""
# <div class="sidebar-footer">
#     <p style="font-size: 19px; text-align: center; color: #47D1FD;"><em>Beta Release</em></p>
#     <hr style="margin-top: 0; margin-bottom: 2px;">
#     <p style="font-size: 15px; text-align: center;">
#         © <a href="https://www.techxos.com" target="_blank" style="text-decoration: none; color: white;">
#         Techxos Digital Solutions 2025</a>
#     </p>
#     <p style="font-size: 17px; text-align: center; margin-bottom: 16px;">
#         <a href="https://www.techxos.com" target="_blank" style="text-decoration: none; color: white;">
#         www.techxos.com</a>
#     </p>
# </div>
# """, unsafe_allow_html=True)

# # -------------------- CUSTOM CSS --------------------
# st.markdown("""
# <style>
#     [data-testid="collapsedControl"] {
#         transform: scale(1.5);
#         margin-top: 10px;
#         margin-left: 8px;
#     }
#     [data-testid="stTextInput"] {
#         margin-top: 20px;
#         margin-bottom: 20px;
#     }
# </style>
# """, unsafe_allow_html=True)




# # FILE: app.py
# import streamlit as st
# from modules.chat_assistant import chat_interface
# from modules.document_reviewer import document_review_ui
# from modules.legal_template import template_builder_ui
# from modules.law_search import law_search_ui
# from modules.query_builder import query_builder_ui
# from utils.auth import get_current_firebase_user, login_required, logout_user
# import os
# from dotenv import load_dotenv
# import firebase_admin
# from firebase_admin import credentials

# # -------------------- LOAD ENV + INIT FIREBASE --------------------
# load_dotenv()

# firebase_key_path = "firebase-service-account.json"

# if not firebase_admin._apps:
#     if os.path.exists(firebase_key_path):
#         cred = credentials.Certificate(firebase_key_path)
#         firebase_admin.initialize_app(cred)
#     else:
#         st.error("❌ Firebase credentials file not found. Please add 'firebase-service-account.json'.")
#         st.stop()

# # -------------------- CONFIG --------------------
# st.set_page_config(page_title="JuristAI - Naija Legal AI Assistant",
#                    page_icon="💎", layout="wide")
# st.title("JuristAI - Naija's no. 1 Legal AI Platform")

# # -------------------- AUTH --------------------
# user = get_current_firebase_user()
# print(f"DEBUG: User object type: {type(user)}, content: {user}")

# # Display login/logout based on authentication status
# if user:
#     st.sidebar.success(f"Welcome {user['full_name']}!")
#     st.sidebar.button("Logout", on_click=logout_user)
# else:
#     st.sidebar.info("Sign in to access all features.")

# # -------------------- SIDEBAR --------------------
# st.sidebar.title("⚖️ Features")
# selection = st.sidebar.radio("Select a tool:", [
#     "📜 Document Review",
#     "💬 AI Chat Assistant",
#     "📝 Legal Template Builder",
#     "🔍 Legal Law Search",
#     "📂 AI Query Panel"
# ])

# # -------------------- TOOL ROUTER --------------------
# if selection == "📜 Document Review":
#     document_review_ui()
# elif selection == "💬 AI Chat Assistant":
#     chat_interface()
# elif selection == "📝 Legal Template Builder":
#     template_builder_ui()
# elif selection == "🔍 Legal Law Search":
#     law_search_ui()
# elif selection == "📂 AI Query Panel":
#     query_builder_ui()

# # -------------------- SIDEBAR FOOTER --------------------
# st.sidebar.markdown("<br><br>", unsafe_allow_html=True)

# st.sidebar.markdown(
#     """
#     <div class="sidebar-footer">
#         <p style="font-size: 19px; text-align: center; color: #47D1FD;"><em>Beta Release</em></p>
#         <hr style="margin-top: 0; margin-bottom: 2px;">
#         <p style="font-size: 15px; text-align: center;">
#             © <a href="https://www.techxos.com" target="_blank" style="text-decoration: none; color: white;">
#             Techxos Digital Solutions 2025</a>
#         </p>
#         <p style="font-size: 17px; text-align: center; margin-bottom: 16px;">
#             <a href="https://www.techxos.com" target="_blank" style="text-decoration: none; color: white;">
#             www.techxos.com</a>
#         </p>
#     </div>
#     """,
#     unsafe_allow_html=True
# )

# # -------------------- CUSTOM CSS --------------------
# st.markdown("""
# <style>
#     [data-testid="collapsedControl"] {
#         transform: scale(1.5);
#         margin-top: 10px;
#         margin-left: 8px;
#     }
#     [data-testid="stTextInput"] {
#         margin-top: 20px;
#         margin-bottom: 20px;
#     }
# </style>
# """, unsafe_allow_html=True)





# # FILE: app.py
# import streamlit as st
# from modules.chat_assistant import chat_interface
# from modules.document_reviewer import document_review_ui
# from modules.legal_template import template_builder_ui
# from modules.law_search import law_search_ui
# from modules.query_builder import query_builder_ui
# from utils.auth import get_current_firebase_user, login_required, logout_user
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # -------------------- CONFIG --------------------
# st.set_page_config(page_title="Naija Legal AI Assistant",
#                    page_icon="💎", layout="wide")
# st.title("Naija's no. 1 Legal AI Platform")

# # -------------------- AUTH --------------------
# user = get_current_firebase_user()
# print(f"DEBUG: User object type: {type(user)}, content: {user}")

# # Display login/logout based on authentication status
# if user:
#     st.sidebar.success(f"Welcome {user['full_name']}!")
#     st.sidebar.button("Logout", on_click=logout_user)
# else:
#     st.sidebar.info("Sign in to access all features.")

# # -------------------- SIDEBAR --------------------
# st.sidebar.title("⚖️ Features")
# selection = st.sidebar.radio("Select a tool:", [
#     "📜 Document Review",
#     "💬 AI Chat Assistant",
#     "📝 Legal Template Builder",
#     "🔍 Legal Law Search",
#     "📂 AI Query Panel"
# ])

# # -------------------- TOOL ROUTER --------------------
# if selection == "📜 Document Review":
#     document_review_ui()
# elif selection == "💬 AI Chat Assistant":
#     chat_interface()
# elif selection == "📝 Legal Template Builder":
#     template_builder_ui()
# elif selection == "🔍 Legal Law Search":
#     law_search_ui()
# elif selection == "📂 AI Query Panel":
#     query_builder_ui()

# # -------------------- SIDEBAR FOOTER --------------------
# st.sidebar.markdown("<br><br>", unsafe_allow_html=True)

# st.sidebar.markdown(
#     """
#     <div class="sidebar-footer">
#         <p style="font-size: 17px; text-align: center; color: #47D1FD;"><em>Beta Release</em></p>
#         <hr style="margin-top: 0; margin-bottom: 5px;">
#         <p style="font-size: 15px; text-align: center;">
#             © <a href="https://www.techxos.com" target="_blank" style="text-decoration: none; color: white;">
#             Techxos Digital Solutions 2025</a>
#         </p>
#     </div>
#     """,
#     unsafe_allow_html=True
# )
# # -------------------- CUSTOM CSS --------------------
# st.markdown("""
# <style>
#     [data-testid="collapsedControl"] {
#         transform: scale(1.5);
#         margin-top: 10px;
#         margin-left: 8px;
#     }
#     /* Custom CSS for the text input box */
#     [data-testid="stTextInput"] {
#         margin-top: 20px;
#         margin-bottom: 20px;
#     }
# </style>
# """, unsafe_allow_html=True)


# # FILE: app.py
# import streamlit as st
# from modules.chat_assistant import chat_interface
# from modules.document_reviewer import document_review_ui
# # from modules.voice_to_text import voice_to_text_ui
# from modules.legal_template import template_builder_ui
# from modules.law_search import law_search_ui
# from modules.query_builder import query_builder_ui

# st.set_page_config(page_title="Naija Legal AI Assistant", layout="wide")
# st.title("Nigeria's No. 1 Legal AI Platform")

# st.sidebar.title("⚖️ Features")
# selection = st.sidebar.radio("Select a tool:", [
#     "📜 Document Review",
#     "💬 AI Chat Assistant",
#     # "🎤 Voice to Text",
#     "📝 Legal Template Builder",
#     "🔍 Legal Law Search",
#     "📂 AI Query Panel"
# ])

# if selection == "📜 Document Review":
#     document_review_ui()
# elif selection == "💬 AI Chat Assistant":
#     chat_interface()
# # elif selection == "🎤 Voice to Text":
# #     voice_to_text_ui()
# elif selection == "📝 Legal Template Builder":
#     template_builder_ui()
# elif selection == "🔍 Legal Law Search":
#     law_search_ui()
# elif selection == "📂 AI Query Panel":
#     query_builder_ui()

# # You'll create each of these modules in the `modules/` folder.

# # .env file should include:
# # GROQ_API_KEY=your_groq_api_key_here


# # # FILE: app.py
# # import streamlit as st
# # from modules.chat_assistant import chat_interface
# # from modules.document_reviewer import document_review_ui
# # from modules.voice_to_text import voice_to_text_ui
# # from modules.legal_template import template_builder_ui
# # from modules.law_search import law_search_ui
# # from modules.query_builder import query_builder_ui

# # st.set_page_config(page_title="Naija Legal AI Assistant", layout="wide")
# # st.title("🇳🇬 Naija Legal AI Platform")

# # st.sidebar.title("⚖️ Features")
# # selection = st.sidebar.radio("Select a tool:", [
# #     "📜 Document Review",
# #     "💬 AI Chat Assistant",
# #     "🎤 Voice to Text",
# #     "📝 Legal Template Builder",
# #     "🔍 Legal Law Search",
# #     "📂 AI Query Panel"
# # ])

# # if selection == "📜 Document Review":
# #     document_review_ui()
# # elif selection == "💬 AI Chat Assistant":
# #     chat_interface()
# # elif selection == "🎤 Voice to Text":
# #     voice_to_text_ui()
# # elif selection == "📝 Legal Template Builder":
# #     template_builder_ui()
# # elif selection == "🔍 Legal Law Search":
# #     law_search_ui()
# # elif selection == "📂 AI Query Panel":
# #     query_builder_ui()

# # # You'll create each of these modules in the `modules/` folder.

# # # .env file should include:
# # # OPENAI_API_KEY=your_openai_key_here
