import asyncio
import httpx
import os
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import json
import re

from core.database import get_db
from models.chat import ChatSession, ChatMessage
from models.user import User
from utils.vector_db import search_similar_chunks

class ChatService:
    def __init__(self, db):
        self.db = db
        self.groq_api_key = os.getenv("GROQ_API_KEY")

    async def process_message(
        self, 
        user_id: str, 
        content: str, 
        country: str = "nigeria"
    ) -> Dict:
        """Process a user message and return AI response (RAG-grounded, corpus-only citations)"""
        # Get conversation history for context
        history = await self._get_conversation_history(user_id)

        # Retrieve top-k relevant chunks from pgvector
        try:
            retrieved = search_similar_chunks(content, k=5)
        except Exception:
            retrieved = []

        # If user asks for decided cases and none exist in corpus, answer without hallucination
        if self._is_case_law_query(content) and not self._retrieval_contains_cases(retrieved):
            msg = (
                "We currently do not have verified decided cases on this subject in the ingested corpus. "
                "You can rely on the applicable statutory framework in our corpus (e.g., Constitution privacy and procedure provisions) or consult an external case-law database for updates."
            )
            message_id = await self._save_message(user_id, content, msg, {"laws": self._laws_from_retrieval(retrieved), "cases": []})
            return {
                "id": message_id,
                "role": "assistant",
                "content": msg,
                "references": {"laws": self._laws_from_retrieval(retrieved), "cases": []},
                "timestamp": datetime.utcnow().isoformat()
            }

        # Apology condition if user clarifies an abbreviation like ATM
        apology = self._needs_apology(history, content)

        # Build grounded prompt with conversation and retrieved context
        prompt = self._create_contextual_prompt(content, history, country, retrieved, apology)

        # Get AI response from Groq (strict, corpus-only)
        response = await self._get_groq_response(prompt)

        # Build references from retrieved sources only (corpus-only)
        references = self._build_references_from_retrieval(retrieved)

        # Save message to database
        message_id = await self._save_message(user_id, content, response, references)

        return {
            "id": message_id,
            "role": "assistant",
            "content": response,
            "references": references,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _create_contextual_prompt(self, user_query: str, history: List[Dict], country: str, retrieved: List, apology: bool) -> str:
        """Create a prompt that includes conversation history and retrieved legal context; enforce corpus-only citations and UX improvements"""
        # Build conversation context
        conversation_context = ""
        if history:
            recent_history = history[-10:]
            conversation_context = "\n\nPrevious conversation:\n"
            for msg in recent_history:
                role = "User" if msg['role'] == 'user' else "Assistant"
                conversation_context += f"{role}: {msg['content']}\n"

        # Build retrieved context as citations
        retrieved_context = ""
        if retrieved:
            retrieved_context = "\n\nCorpus context (cite ONLY from these; do NOT invent citations):\n" + "\n".join(
                [f"- [{os.path.basename(str(r[2]))}] {str(r[1])[:600]}" for r in retrieved]
            )

        rules = (
            "Rules (STRICT):\n"
            "- Cite ONLY provisions/sections that appear in the corpus context above.\n"
            "- Do NOT cite cases unless they appear in the corpus context.\n"
            "- If the user asks for cases and none are in corpus, state that no verified cases are in the corpus and provide statutory analysis only.\n"
            "- If a specific section/citation is not present in the retrieved text, do not fabricate it; say 'Not available in corpus.'\n"
            "- Lead with a one-sentence direct rule; then short analysis grounded in the corpus; then practical next steps.\n"
            "- No apologies or disclaimers unless the user explicitly clarifies a prior misunderstanding; in that case, begin with a single brief apology (one line) and proceed.\n"
            "- End with 'Suggested next questions' (2-3 bullets) that you can answer from the above corpus context only; if insufficient corpus, omit this section.\n"
        )

        apology_line = (
            "If the user clarified an abbreviation (e.g., 'ATM' meaning 'awaiting trial inmate/man'), begin with: 'Thanks for the clarification — I misunderstood earlier.'"
            if apology else ""
        )

        return f"""You are a {country.title()} legal expert AI assistant. Provide a strictly corpus-grounded answer.

{rules}
{apology_line}
{conversation_context}
{retrieved_context}

Question: {user_query}

Answer format: (1) Direct rule in one sentence. (2) Focused legal basis with corpus citations. (3) Short practical next steps. (4) Suggested next questions (only if answerable from corpus)."""

    async def _get_groq_response(self, prompt: str) -> str:
        """Get response from Groq API with strict fallback that avoids hallucination"""
        if not self.groq_api_key:
            return (
                "Corpus-grounded: No external model available. Use the provided corpus context to derive the rule. If a citation is not present in the corpus, state 'Not available in corpus.'"
            )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.groq_api_key}"
                    },
                    json={
                        "model": "llama3-8b-8192",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                        "max_tokens": 1500
                    },
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return (
                        "Corpus-grounded: Unable to reach model. Provide the rule and analysis only if present in corpus context; otherwise say 'Not available in corpus.'"
                    )
        except Exception:
            return (
                "Corpus-grounded: Model error. Provide the rule and analysis only if present in corpus context; otherwise say 'Not available in corpus.'"
            )

    def _build_references_from_retrieval(self, retrieved: List) -> Dict:
        """Create a references object from retrieved chunks (corpus-only)"""
        if not retrieved:
            return {"laws": [], "cases": []}
        laws = []
        cases = []
        seen = set()
        for row in retrieved:
            # row: (id, text, source)
            text = str(row[1])
            source = os.path.basename(str(row[2]))
            # Try to extract a section reference
            m = re.search(r"section\s+[\dA-Za-z\-]+", text, flags=re.IGNORECASE)
            section = f" ({m.group(0).strip()})" if m else ""
            title = f"{source}{section}"
            key = title.lower().strip()
            if key in seen:
                continue
            seen.add(key)
            laws.append(title)
        return {"laws": laws[:10], "cases": cases}

    def _laws_from_retrieval(self, retrieved: List) -> List[str]:
        refs = self._build_references_from_retrieval(retrieved)
        return refs.get("laws", [])

    def _retrieval_contains_cases(self, retrieved: List) -> bool:
        # If corpus includes case PDFs, you can detect by filename patterns or ' v. '
        for row in retrieved:
            text = str(row[1])
            source = str(row[2]).lower()
            if " v " in text.lower() or ".v." in text.lower() or " v." in text.lower() or " v " in source:
                return True
        return False

    def _is_case_law_query(self, text: str) -> bool:
        return bool(re.search(r"\b(case|cases|precedent|authorities|judgment|decision)\b", text, flags=re.IGNORECASE))

    def _needs_apology(self, history: List[Dict], content: str) -> bool:
        # Apologize if the user explicitly clarifies a term (e.g., ATM) after a likely misunderstanding
        text = content.lower()
        if "i mean" in text or "no i mean" in text or "by atm i mean" in text:
            return True
        # Also, if abbreviation ATM appears and prior context mentions detention/remand
        if re.search(r"\batm\b", text, flags=re.IGNORECASE):
            for msg in reversed(history[-5:]):
                if any(kw in msg.get('content', '').lower() for kw in ["detain", "remand", "awaiting trial", "custody"]):
                    return True
        return False

    async def _get_conversation_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get recent conversation history for context"""
        try:
            messages = self.db.query(ChatMessage).filter(
                ChatMessage.user_id == user_id
            ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
            messages.reverse()
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []

    async def _save_message(self, user_id: str, user_content: str, ai_response: str, references: Dict) -> str:
        """Save message to database"""
        message_id = str(uuid.uuid4())
        session = await self._get_or_create_session(user_id)
        user_message = ChatMessage(
            id=message_id + "_user",
            session_id=session.id,
            user_id=user_id,
            role="user",
            content=user_content,
            timestamp=datetime.utcnow()
        )
        ai_message = ChatMessage(
            id=message_id + "_ai",
            session_id=session.id,
            user_id=user_id,
            role="assistant",
            content=ai_response,
            references=json.dumps(references),
            timestamp=datetime.utcnow()
        )
        self.db.add(user_message)
        self.db.add(ai_message)
        self.db.commit()
        return message_id

    async def _get_or_create_session(self, user_id: str) -> ChatSession:
        """Get existing session or create a new one for the user"""
        session = self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.created_at.desc()).first()
        if not session:
            session = ChatSession(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title="Legal Consultation",
                created_at=datetime.utcnow()
            )
            self.db.add(session)
            self.db.commit()
        return session

    async def get_chat_history(self, user_id: str, session_id: Optional[str] = None) -> List[Dict]:
        """Get chat history for user"""
        query = self.db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
        if session_id:
            query = query.filter(ChatMessage.session_id == session_id)
        messages = query.order_by(ChatMessage.timestamp).all()
        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "references": json.loads(msg.references) if msg.references else None,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]

    async def get_sessions(self, user_id: str) -> List[Dict]:
        """Get all chat sessions for a user"""
        sessions = self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.created_at.desc()).all()
        return [
            {
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at.isoformat()
            }
            for session in sessions
        ]

    async def create_session(self, user_id: str, title: str) -> Dict:
        """Create a new chat session"""
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            created_at=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        return {
            "id": session.id,
            "title": session.title,
            "created_at": session.created_at.isoformat()
        }
