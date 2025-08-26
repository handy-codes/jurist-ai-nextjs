# === FILE: modules/chat_assistant.py ===
import streamlit as st
import requests
import os
import time
import re
from dotenv import load_dotenv
from utils.db_utils import log_query, log_feedback, get_or_create_chat_session, save_chat_message, load_chat_history
from utils.auth import get_current_firebase_user, login_required
from config.database import SessionLocal
from utils.vector_db import search_similar_chunks as search_chunks

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ------------------ UTILITIES ------------------

def extract_document_references(text):
    """Extract only real references that exist in our database"""
    law_pattern = r'(?:Section|Sections?)\s+\d+(?:-\d+)?(?:\s+and\s+\d+)?\s+of\s+the\s+([A-Za-z\s]+(?:Act|Law|Code|Regulation))'
    case_pattern = r'(?:case of|in\s+)?([A-Za-z\s]+v\.\s+[A-Za-z\s]+)'
    laws = re.findall(law_pattern, text)
    cases = re.findall(case_pattern, text)
    
    # Filter to only include references that exist in our database
    verified_laws = []
    verified_cases = []
    
    # Check laws against database
    for law in set(laws):
        if verify_reference_exists(law, "law"):
            verified_laws.append(law)
    
    # Check cases against database  
    for case in set(cases):
        if verify_reference_exists(case, "case"):
            verified_cases.append(case)
    
    return {'laws': verified_laws, 'cases': verified_cases}

def verify_reference_exists(reference, ref_type):
    """Verify if a reference exists in our legal documents database"""
    try:
        with SessionLocal() as db:
            if ref_type == "law":
                # Search for law references in legal_chunks
                result = db.execute(
                    "SELECT COUNT(*) FROM legal_chunks WHERE text ILIKE %s",
                    (f"%{reference}%",)
                ).scalar()
            else:  # case
                result = db.execute(
                    "SELECT COUNT(*) FROM legal_chunks WHERE text ILIKE %s",
                    (f"%{reference}%",)
                ).scalar()
            return result > 0
    except Exception as e:
        st.error(f"Error verifying reference: {e}")
        return False

def format_response(text):
    """Format response with proper markdown and structure"""
    # Remove any disclaimers or off-point statements
    text = remove_disclaimers(text)
    
    # Format legal citations properly
    text = format_legal_citations(text)
    
    return text

def remove_disclaimers(text):
    """Remove common disclaimers and off-point statements"""
    disclaimer_patterns = [
        r"I don't have access to.*",
        r"I cannot provide.*",
        r"Please consult.*",
        r"I am not a lawyer.*",
        r"This is not legal advice.*",
        r"I cannot give legal advice.*",
        r"Please seek professional.*",
        r"I don't have recent.*",
        r"I cannot cite.*",
        r"Based on my training.*"
    ]
    
    for pattern in disclaimer_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    return text.strip()

def format_legal_citations(text):
    """Format legal citations for better readability"""
    # Format section references
    text = re.sub(r'(Section\s+\d+)', r'**\1**', text)
    text = re.sub(r'(Act\s+\d+)', r'**\1**', text)
    
    # Format case names
    text = re.sub(r'([A-Za-z\s]+v\.\s+[A-Za-z\s]+)', r'*\1*', text)
    
    return text

def get_context_from_db(user_query, k=4):
    """Get relevant context from database with enhanced search"""
    results = search_chunks(user_query, k=k)
    
    if not results:
        return "No specific legal references found in the database for this query."
    
    context = "\n\n".join([r[1] for r in results])
    return context

def estimate_tokens(text):
    """Simple token estimation (1 token ~ 4 characters)"""
    return max(20, len(text) // 4)

def summarize_history(history):
    """Create a concise summary of conversation history for context"""
    if len(history) <= 5:
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

    # Keep first message, last 4 messages, and a summary placeholder
    summary = f"{history[0]['role']}: {history[0]['content']}\n... [previous conversation summarized] ...\n"
    summary += "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-4:]])
    return summary

def create_enhanced_prompt(user_query, context, history_summary):
    """Create an enhanced prompt that maintains context and prevents hallucination"""
    return f"""
You are a Nigerian legal expert AI assistant. Your responses must:

1. **ONLY cite references that exist in the provided legal context**
2. **Maintain conversation context** from the history
3. **Answer follow-up questions** without disclaimers
4. **If asked for specific cases/rulings not in context, say**: "I don't have recent reference rulings to cite for that specific case in my current legal database."
5. **Provide direct, actionable legal information** based on Nigerian law
6. **Use the conversation history** to understand context and provide relevant answers

Legal Context (from database):
{context}

Conversation History:
{history_summary}

Current Question:
{user_input}

Instructions:
- Answer directly without disclaimers
- Cite only laws/cases from the provided context
- If information is not in context, acknowledge it clearly
- Maintain conversation flow and context
- Provide practical legal guidance based on Nigerian law
"""

# ------------------ MAIN CHAT UI ------------------

@login_required
def chat_interface():
    user = get_current_firebase_user()
    user_name = user.get("full_name", "User") if user else "User"
    user_id = user.get("id")

    if not user_id or not st.session_state.get("current_chat"):
        st.warning("No chat session found. Please select or create a new chat from the sidebar.")
        return

    with SessionLocal() as db:
        session_id = st.session_state.current_chat
        chat_session = get_or_create_chat_session(db, user_id, session_id)

        # Load chat history from DB if not already in session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = load_chat_history(db, chat_session.id)

    st.markdown("""
    <style>
    .chat-scroll {
        max-height: calc(100vh - 320px);
        overflow-y: auto;
        padding: 10px;
        border-radius: 10px;
        background-color: #0e1117;
    }
    .user-message {
        background-color: #005fcc;
        color: white;
        border-radius: 15px 15px 0 15px;
        padding: 12px 15px;
        margin: 8px 0;
        max-width: 80%;
        align-self: flex-end;
    }
    .assistant-message {
        background-color: #333;
        color: white;
        border-radius: 15px 15px 15px 0;
        padding: 12px 15px;
        margin: 8px 0;
        max-width: 80%;
        align-self: flex-start;
    }
    .references {
        font-size: 0.85em;
        color: #aaa;
        margin-top: 5px;
        padding-left: 10px;
        border-left: 2px solid #47D1FD;
    }
    .feedback-section {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        border: 1px solid #333;
    }
    .feedback-buttons {
        display: flex;
        gap: 10px;
        align-items: center;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.header("💬 JuristAI — Nigerian Legal Assistant")

    # Chat scrollable window
    with st.container():
        st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            role = msg["role"]
            content = msg["content"]
            refs = msg.get("references", {})

            if role == "user":
                st.markdown(f"<div class='user-message'>{content}</div>", unsafe_allow_html=True)
            elif role == "assistant":
                st.markdown(f"<div class='assistant-message'>{content}</div>", unsafe_allow_html=True)

                # Show verified references only
                if refs and (refs.get('laws') or refs.get('cases')):
                    ref_html = "<div class='references'><strong>📚 Verified References:</strong><br>"
                    if refs.get('laws'):
                        ref_html += "<strong>Laws:</strong><br>" + "<br>".join([f"• {law}" for law in refs['laws']]) + "<br>"
                    if refs.get('cases'):
                        ref_html += "<strong>Cases:</strong><br>" + "<br>".join([f"• {case}" for case in refs['cases']])
                    ref_html += "</div>"
                    st.markdown(ref_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Chat input (sticky bottom)
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([8, 2])
        with col1:
            user_input = st.text_input(
                "Ask a legal question", 
                label_visibility="collapsed", 
                placeholder="Type your legal question..."
            )
        with col2:
            submitted = st.form_submit_button("Ask")

    if submitted and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with SessionLocal() as db:
            save_chat_message(db, chat_session.id, "user", user_input)

        with st.spinner("Consulting Nigerian law..."):
            try:
                # Get context with enhanced search
                context = get_context_from_db(user_input, k=4)

                # Create smarter history summary
                history_summary = summarize_history(st.session_state.chat_history)

                # Build enhanced prompt
                prompt = create_enhanced_prompt(user_input, context, history_summary)

                # Estimate tokens and optimize if needed
                total_tokens = estimate_tokens(prompt)
                if total_tokens > 5500:
                    # Truncate context but preserve history
                    context = context[:3000] + "... [truncated context]"
                    prompt = create_enhanced_prompt(user_input, context, history_summary)

                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {GROQ_API_KEY}"
                }
                payload = {
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "system", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 1500
                }
                
                response = requests.post(url, headers=headers, json=payload)
                data = response.json()

                if response.status_code != 200:
                    error_msg = data.get('error', {}).get('message', 'Unknown API error')

                    # Handle token limit error with fallback
                    if "too large" in error_msg.lower() or "tokens" in error_msg.lower():
                        fallback_prompt = f"""
Based on our conversation history, answer concisely as a Nigerian legal expert:

History:
{history_summary[-2000:]}

Question:
{user_input}

Remember: Only cite references from provided context, maintain conversation flow.
"""
                        payload["messages"][0]["content"] = fallback_prompt
                        fallback_response = requests.post(url, headers=headers, json=payload)
                        fallback_data = fallback_response.json()

                        if fallback_response.status_code == 200:
                            answer = fallback_data['choices'][0]['message']['content']
                        else:
                            st.error("⚠️ Question too complex. Please ask a more specific question.")
                            return
                    else:
                        st.error(f"❌ API Error: {error_msg}")
                        return
                else:
                    answer = data['choices'][0]['message']['content']

                # Format and extract verified references
                formatted = format_response(answer)
                references = extract_document_references(answer)

                # Store the query ID for feedback
                with SessionLocal() as db:
                    query_id = log_query(db, user_id, user_input, formatted, str(references), 0.0)
                    st.session_state.last_query_id = query_id

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": formatted,
                    "references": references
                })

                with SessionLocal() as db:
                    save_chat_message(db, chat_session.id, "assistant", formatted, references)

            except Exception as e:
                st.error(f"❌ System Error: {str(e)}")

    # ------------------ FEEDBACK SYSTEM (INTEGRATED AT BOTTOM) ------------------
    
    # Show feedback section only if there's an assistant message
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
        st.markdown("---")
        
        # Feedback section with enhanced styling
        st.markdown("""
        <div class="feedback-section">
            <h4>📝 Was this answer helpful?</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 8])
        
        with col1:
            if st.button("👍 Yes", key="yes_btn", help="This answer was helpful"):
                with SessionLocal() as db:
                    log_feedback(db, user_id, st.session_state.last_query_id, 5, True)
                st.success("✅ Thanks for your feedback!")
                st.rerun()
                
        with col2:
            if st.button("👎 No", key="no_btn", help="This answer was not helpful"):
                with SessionLocal() as db:
                    log_feedback(db, user_id, st.session_state.last_query_id, 1, False)
                st.info("📝 We'll use your feedback to improve.")
                st.rerun()
                
        with col3:
            feedback_text = st.text_input(
                "💡 How can I improve? I'm still learning Nigerian law",
                key="extra_feedback",
                label_visibility="collapsed",
                placeholder="Suggest improvements or point out issues..."
            )
            if st.button("Submit Feedback", key="extra_submit") and feedback_text:
                with SessionLocal() as db:
                    log_feedback(db, user_id, st.session_state.last_query_id, 0, False, feedback_text)
                st.success("🎯 Extra feedback received! Thank you for helping improve JuristAI.")
                st.rerun()

    # Clear chat button in sidebar
    if st.sidebar.button("🧹 Clear Chat History"):
        st.session_state.chat_history = [st.session_state.chat_history[0]]
        st.rerun()
