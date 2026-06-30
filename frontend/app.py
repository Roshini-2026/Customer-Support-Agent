"""
Airtel Customer Support Agent — Professional Real Brand Chatbot UI
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datetime
import subprocess
import html as _html
import streamlit as st

try:
    import pyperclip
    _HAS_PYPERCLIP = True
except ImportError:
    _HAS_PYPERCLIP = False
from agent import run_customer_support

# ─────────────────────────────────────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Airtel Customer Support Agent",
    page_icon="📡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
#  Session state
# ─────────────────────────────────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "editing_idx" not in st.session_state: st.session_state.editing_idx = None

has_chat = len(st.session_state.messages) > 0

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── Hide all Streamlit chrome ── */
#MainMenu, footer, header               { visibility: hidden; }
section[data-testid="stSidebar"]       { display: none !important; }
div[data-testid="collapsedControl"]    { display: none !important; }
button[data-testid="baseButton-header"]{ display: none !important; }

/* ── Background ── */
.stApp {
    background: #0f0f0f;
    background-image:
        radial-gradient(ellipse 70% 45% at 50% 0%, rgba(237,28,36,0.10) 0%, transparent 65%),
        radial-gradient(ellipse 40% 30% at 90% 100%, rgba(180,10,20,0.07) 0%, transparent 60%);
    background-attachment: fixed;
    min-height: 100vh;
}

/* ── Scrollbar ── */
::-webkit-scrollbar             { width: 5px; }
::-webkit-scrollbar-track       { background: transparent; }
::-webkit-scrollbar-thumb       { background: #2a2a2a; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #3d3d3d; }

/* ── Main container ── */
.block-container {
    max-width: 760px !important;
    padding-top: 0 !important;
    padding-bottom: 145px !important;
    margin: 0 auto;
}

/* ══════════════════════════════════════════════════════
   TOP NAVIGATION BAR
══════════════════════════════════════════════════════ */
.top-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 58px;
    background: rgba(15,15,15,0.92);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.top-nav-inner { display: flex; align-items: center; gap: 12px; }
.airtel-logo-mark {
    width: 34px; height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ED1C24 0%, #b01018 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
    box-shadow: 0 2px 12px rgba(237,28,36,0.45);
}
.top-nav-text { display: flex; flex-direction: column; gap: 1px; }
.top-nav-title {
    font-size: 0.92rem; font-weight: 600; color: #ffffff;
    letter-spacing: -0.1px; line-height: 1;
}
.top-nav-status {
    display: flex; align-items: center; gap: 5px;
    font-size: 0.68rem; color: #888; font-weight: 400;
}
.status-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #22c55e; box-shadow: 0 0 6px rgba(34,197,94,0.8); flex-shrink: 0;
}
.header-spacer { height: 58px; }

/* ══════════════════════════════════════════════════════
   HERO — empty state
══════════════════════════════════════════════════════ */
.hero-outer {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 60vh; text-align: center;
    padding: 3rem 1.5rem 2rem;
}
.hero-avatar {
    width: 80px; height: 80px; border-radius: 50%;
    background: linear-gradient(145deg, #1a1a1a, #111);
    border: 2px solid rgba(237,28,36,0.4);
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem; margin-bottom: 1.8rem;
    box-shadow: 0 0 0 6px rgba(237,28,36,0.06), 0 0 0 12px rgba(237,28,36,0.03), 0 12px 40px rgba(0,0,0,0.5);
}
.hero-greeting {
    font-size: 0.78rem; font-weight: 600; color: #ED1C24;
    letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 0.7rem;
}
.hero-title {
    font-size: 2rem; font-weight: 700; color: #ffffff;
    letter-spacing: -0.5px; line-height: 1.25; margin-bottom: 0.85rem;
}
.hero-desc {
    font-size: 0.93rem; color: #5a5a5a; line-height: 1.7;
    max-width: 380px; font-weight: 400;
}

/* ══════════════════════════════════════════════════════
   CHAT MESSAGES
══════════════════════════════════════════════════════ */
div[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 4px 0 !important;
}

/* User bubble */
.user-bubble {
    background: #1e1e1e;
    border: 1px solid #2e2e2e;
    border-radius: 20px 20px 4px 20px;
    padding: 12px 18px;
    color: #e8e8e8;
    font-size: 0.95rem;
    line-height: 1.65;
    word-wrap: break-word;
    word-break: break-word;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    font-weight: 400;
    max-width: 90%;
    margin-left: auto;
}

/* ── Action buttons row (Streamlit native buttons styled) ── */
.action-row {
    display: flex;
    justify-content: flex-end;
    gap: 4px;
    margin-top: 5px;
    padding-right: 2px;
}

/* Override Streamlit button styles for action buttons */
[data-testid="stHorizontalBlock"] .action-btn-col .stButton > button,
.action-btn-col .stButton > button {
    width: 28px !important;
    height: 28px !important;
    min-height: 28px !important;
    padding: 0 !important;
    border-radius: 7px !important;
    background: #1a1a1a !important;
    border: 1px solid #2e2e2e !important;
    color: #606060 !important;
    font-size: 14px !important;
    line-height: 1 !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}
[data-testid="stHorizontalBlock"] .action-btn-col .stButton > button:hover,
.action-btn-col .stButton > button:hover {
    background: #262626 !important;
    border-color: #444 !important;
    color: #cccccc !important;
    transform: scale(1.08) !important;
}

/* Edit-mode inline editor */
.edit-container {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
    margin-left: auto;
    max-width: 92%;
}
.edit-container .stTextArea textarea {
    background: #1e1e1e !important;
    border: 1px solid #2e2e2e !important;
    border-radius: 14px !important;
    box-shadow: none !important;
    color: #e8e8e8 !important;
    font-size: 0.95rem !important;
    font-family: 'Inter', sans-serif !important;
    line-height: 1.65 !important;
    resize: none !important;
    caret-color: #ED1C24 !important;
    padding: 12px 16px !important;
    outline: none !important;
}
.edit-container .stTextArea textarea:focus {
    border-color: #3a3a3a !important;
    box-shadow: none !important;
    outline: none !important;
}
/* Hide the red focus ring Streamlit adds to its textarea wrapper */
.edit-container [data-baseweb="textarea"],
.edit-container [data-baseweb="base-input"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}
.edit-container label { display: none !important; }

/* Edit action buttons — compact pill style */
.edit-send-btn > div > .stButton > button {
    background: linear-gradient(135deg, #ED1C24, #c0121a) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-size: 0.70rem !important;
    font-weight: 600 !important;
    height: 22px !important;
    min-height: 22px !important;
    line-height: 1 !important;
    padding: 0 10px !important;
    box-shadow: 0 1px 6px rgba(237,28,36,0.35) !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.2px !important;
}
.edit-send-btn > div > .stButton > button:hover {
    box-shadow: 0 2px 10px rgba(237,28,36,0.55) !important;
    transform: scale(1.04) !important;
}
.edit-cancel-btn > div > .stButton > button {
    background: #1a1a1a !important;
    color: #666 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
    font-size: 0.70rem !important;
    height: 22px !important;
    min-height: 22px !important;
    line-height: 1 !important;
    padding: 0 10px !important;
    transition: all 0.15s ease !important;
}
.edit-cancel-btn > div > .stButton > button:hover {
    background: #222 !important;
    color: #aaa !important;
    border-color: #3a3a3a !important;
}

/* Timestamp */
.msg-time {
    font-size: 0.6rem; color: #333;
    margin-top: 5px; padding: 0 4px;
    text-align: right;
}

/* Agent response card */
.agent-card {
    background: #161616;
    border: 1px solid #242424;
    border-radius: 4px 20px 20px 20px;
    padding: 16px 20px;
    color: #d4d4d4;
    font-size: 0.94rem;
    line-height: 1.8;
    word-wrap: break-word;
    word-break: break-word;
    box-shadow: 0 2px 20px rgba(0,0,0,0.4);
}

/* Tags */
.tag-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.tag {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 20px;
    font-size: 0.62rem; font-weight: 700;
    letter-spacing: 0.7px; text-transform: uppercase;
}
.tag-cat { background: rgba(237,28,36,0.12); color: #f87171; border: 1px solid rgba(237,28,36,0.25); }
.tag-pos { background: rgba(34,197,94,0.10);  color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
.tag-neg { background: rgba(237,28,36,0.12); color: #f87171; border: 1px solid rgba(237,28,36,0.25); }
.tag-neu { background: rgba(234,179,8,0.10);  color: #fbbf24; border: 1px solid rgba(234,179,8,0.25); }

/* Agent name */
.agent-name {
    font-size: 0.68rem; font-weight: 700; color: #ED1C24;
    letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 6px; display: flex; align-items: center; gap: 5px;
}

/* ══════════════════════════════════════════════════════
   BOTTOM INPUT AREA
══════════════════════════════════════════════════════ */
div[data-testid="stBottomBlockContainer"],
div[data-testid="stBottom"] {
    background: linear-gradient(to top, #0f0f0f 60%, transparent) !important;
    border: none !important;
    box-shadow: none !important;
    padding-bottom: 28px !important;
    padding-top: 0 !important;
}

div[data-testid="stChatInput"] {
    max-width: 760px !important;
    margin: 0 auto !important;
    background: #1c1c1c !important;
    border-radius: 14px !important;
    border: 1px solid #2a2a2a !important;
    box-shadow: 0 4px 30px rgba(0,0,0,0.5) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: rgba(237,28,36,0.4) !important;
    box-shadow: 0 0 0 3px rgba(237,28,36,0.08), 0 4px 30px rgba(0,0,0,0.5) !important;
}
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] form,
div[data-testid="stChatInput"] > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
div[data-testid="stChatInput"] textarea {
    color: #f0f0f0 !important;
    font-size: 0.96rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 14px 16px !important;
    line-height: 1.6 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    resize: none !important;
    caret-color: #ffffff !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: #909090 !important;
    opacity: 1 !important;
}

/* Send button */
div[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, #ED1C24, #c0121a) !important;
    border-radius: 10px !important;
    width: 36px !important; height: 36px !important;
    margin: 8px 8px 8px 4px !important;
    border: none !important;
    box-shadow: 0 3px 12px rgba(237,28,36,0.45) !important;
    transition: all 0.18s ease !important;
    flex-shrink: 0 !important;
}
div[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"]:hover {
    background: linear-gradient(135deg, #ff2d35, #ED1C24) !important;
    transform: scale(1.07) !important;
    box-shadow: 0 5px 18px rgba(237,28,36,0.6) !important;
}
div[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] svg {
    fill: #fff !important; width: 15px !important; height: 15px !important;
}

/* Spinner */
div[data-testid="stSpinner"] > div { border-top-color: #ED1C24 !important; }

@media (max-width: 600px) {
    .hero-title { font-size: 1.5rem; }
    .hero-avatar { width: 64px; height: 64px; font-size: 1.7rem; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  Helper: copy text to Windows clipboard reliably (server-side)
# ─────────────────────────────────────────────────────────────────────────────
def _copy_to_clipboard(text: str) -> bool:
    """Copy text to the local system clipboard. Returns True on success."""
    # 1. Try pyperclip (cross-platform, most reliable)
    if _HAS_PYPERCLIP:
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            pass
    # 2. Fallback: Windows 'clip' command via subprocess
    try:
        subprocess.run(
            ["clip"],
            input=text.encode("utf-16-le"),
            check=True,
            timeout=3,
        )
        return True
    except Exception:
        pass
    return False

# ─────────────────────────────────────────────────────────────────────────────
#  Top nav bar
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-nav">
    <div class="top-nav-inner">
        <div class="airtel-logo-mark">📡</div>
        <div class="top-nav-text">
            <span class="top-nav-title">Airtel Customer Support Agent</span>
            <span class="top-nav-status">
                <span class="status-dot"></span>
                Online · Always available
            </span>
        </div>
    </div>
</div>
<div class="header-spacer"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  Empty-state hero
# ─────────────────────────────────────────────────────────────────────────────
if not has_chat:
    st.markdown("""
    <div class="hero-outer">
        <div class="hero-avatar">📡</div>
        <div class="hero-greeting">Airtel Support</div>
        <h1 class="hero-title">Airtel Customer Support Agent</h1>
        <p class="hero-desc">
            I can help you with network issues, billing queries,
            recharge plans, SIM activation, and more.
            Type your question below to get started.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  Chat history
# ─────────────────────────────────────────────────────────────────────────────
for i, msg in enumerate(st.session_state.messages):

    # ── USER MESSAGE ──────────────────────────────────────────────────────────
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑"):

            # ── EDIT MODE ─────────────────────────────────────────────────────
            if st.session_state.editing_idx == i:
                st.markdown('<div class="edit-container">', unsafe_allow_html=True)

                edited_text = st.text_area(
                    label="edit",
                    value=msg["content"],
                    key=f"edit_ta_{i}",
                    label_visibility="collapsed",
                    height=90,
                )

                st.markdown('</div>', unsafe_allow_html=True)

                # Send / Cancel buttons
                _c_send, _c_cancel, _c_space = st.columns([2, 2, 8])
                with _c_send:
                    st.markdown('<div class="edit-send-btn">', unsafe_allow_html=True)
                    if st.button("↑ Send", key=f"edit_send_{i}"):
                        if edited_text and edited_text.strip():
                            _new_text = edited_text.strip()
                            # Truncate history from this message onward (ChatGPT-style)
                            st.session_state.messages = st.session_state.messages[:i]
                            st.session_state.editing_idx = None
                            _now = datetime.datetime.now().strftime("%I:%M %p")
                            st.session_state.messages.append({
                                "role":    "user",
                                "content": _new_text,
                                "time":    _now,
                            })
                            with st.spinner("Airtel Support is typing…"):
                                _result = run_customer_support(_new_text)
                            st.session_state.messages.append({
                                "role":      "assistant",
                                "content":   _result["response"],
                                "category":  _result["category"],
                                "sentiment": _result["sentiment"],
                                "time":      _now,
                            })
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                with _c_cancel:
                    st.markdown('<div class="edit-cancel-btn">', unsafe_allow_html=True)
                    if st.button("✕ Cancel", key=f"edit_cancel_{i}"):
                        st.session_state.editing_idx = None
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            # ── NORMAL VIEW ───────────────────────────────────────────────────
            else:
                # Bubble
                st.markdown(
                    f'<div class="user-bubble">{_html.escape(msg["content"])}</div>',
                    unsafe_allow_html=True,
                )

                # Action buttons: push copy & edit to the right
                _space_col, _copy_col, _edit_col = st.columns([12, 1, 1])

                with _copy_col:
                    st.markdown('<div class="action-btn-col">', unsafe_allow_html=True)
                    if st.button("⧉", key=f"copy_{i}", help="Copy message"):
                        _ok = _copy_to_clipboard(msg["content"])
                        if _ok:
                            st.toast("✅ Copied!", icon="📋")
                        else:
                            st.toast("⚠️ Could not copy automatically.", icon="⚠️")
                    st.markdown('</div>', unsafe_allow_html=True)

                with _edit_col:
                    st.markdown('<div class="action-btn-col">', unsafe_allow_html=True)
                    if st.button("✎", key=f"edit_btn_{i}", help="Edit & resend"):
                        st.session_state.editing_idx = i
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                if "time" in msg:
                    st.markdown(
                        f'<div class="msg-time">{msg["time"]}</div>',
                        unsafe_allow_html=True,
                    )

    # ── ASSISTANT MESSAGE ─────────────────────────────────────────────────────
    else:
        sentiment = msg.get("sentiment", "Neutral")
        category  = msg.get("category", "")

        sent_cls  = {"Positive": "tag-pos", "Negative": "tag-neg", "Neutral": "tag-neu"}.get(sentiment, "tag-neu")
        sent_icon = {"Positive": "😊", "Negative": "😠", "Neutral": "😐"}.get(sentiment, "😐")
        cat_icon  = {"Technical": "🔧", "Billing": "💳", "General": "ℹ️"}.get(category, "💬")

        tags_html = (
            f'<div class="tag-row">'
            f'<span class="tag tag-cat">{cat_icon} {category}</span>'
            f'<span class="tag {sent_cls}">{sent_icon} {sentiment}</span>'
            f'</div>'
        )
        agent_label = '<div class="agent-name">📡 Airtel Support</div>'

        with st.chat_message("assistant", avatar="📡"):
            st.markdown(
                f'<div class="agent-card">{agent_label}{tags_html}{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
            if "time" in msg:
                st.markdown(
                    f'<div class="msg-time">{msg["time"]}</div>',
                    unsafe_allow_html=True,
                )

# ─────────────────────────────────────────────────────────────────────────────
#  Chat input
# ─────────────────────────────────────────────────────────────────────────────
query = st.chat_input("Type your question here…")

if query:
    now = datetime.datetime.now().strftime("%I:%M %p")

    st.session_state.messages.append({
        "role":    "user",
        "content": query,
        "time":    now,
    })

    with st.spinner("Airtel Support is typing…"):
        result = run_customer_support(query)

    st.session_state.messages.append({
        "role":      "assistant",
        "content":   result["response"],
        "category":  result["category"],
        "sentiment": result["sentiment"],
        "time":      now,
    })

    st.rerun()