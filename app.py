from dotenv import load_dotenv
load_dotenv()
from typing import Optional
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
import io
import os
import base64
import google.generativeai as genai

st.set_page_config(
    page_title="Gen AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

api_key = os.getenv("API_KEY")
if not api_key:
    st.error("❌ API Key missing. Check your .env file.")
    st.stop()

genai.configure(api_key=api_key)

FREE_TOKEN_LIMIT = 1_000_000

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Lora:ital,wght@0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:        #F7F6F3;
  --bg2:       #FFFFFF;
  --bg3:       #F0EEE9;
  --border:    #E4E1DA;
  --border2:   #D4D0C8;
  --text1:     #1C1917;
  --text2:     #44403C;
  --text3:     #78716C;
  --accent:    #4B5FD6;
  --accent2:   #6B7FE8;
  --accent-bg: #EEF0FB;
  --accent-bg2:#E5E8F8;
  --success:   #16A34A;
  --warn:      #D97706;
  --danger:    #DC2626;
  --danger-bg: #FEF2F2;
  --code-bg:   #F5F3EE;
  --shadow-sm: 0 1px 3px rgba(28,25,23,0.06), 0 1px 2px rgba(28,25,23,0.04);
  --shadow-md: 0 4px 16px rgba(28,25,23,0.08), 0 1px 4px rgba(28,25,23,0.04);
  --shadow-lg: 0 12px 40px rgba(28,25,23,0.10), 0 4px 12px rgba(28,25,23,0.06);
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --font-sans: 'DM Sans', sans-serif;
  --font-serif: 'Lora', serif;
  --font-mono: 'JetBrains Mono', monospace;
}

/* ── APP SHELL ── */
.stApp {
  background: var(--bg) !important;
  font-family: var(--font-sans) !important;
}
header[data-testid="stHeader"],
[data-testid="stHeader"] {
  background: var(--bg) !important;
  border-bottom: 1px solid var(--border) !important;
}
[data-testid="stHeader"] button,
[data-testid="stHeader"] svg {
  color: var(--text3) !important;
  fill: var(--text3) !important;
}

[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
[data-testid="stChatInputContainer"],
div[class*="stBottom"] { background: transparent !important; }
[data-testid="stBottom"] > div {
  background: linear-gradient(0deg, var(--bg) 55%, transparent 100%) !important;
  backdrop-filter: blur(18px) !important;
  border-top: none !important;
  padding-bottom: 12px !important;
}

.main .block-container {
  max-width: 900px !important;
  padding: 1.5rem 1.5rem 220px !important;
}

.stApp, .stApp p, .stApp span, .stApp div, .stApp label,
.stApp li, .stApp td, .stApp th {
  color: var(--text1) !important;
  font-family: var(--font-sans) !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: var(--text1) !important; }

/* ══════════════════════════════════════════
   SIDEBAR — Fixed text visibility
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: #0F0F0F !important;
  border-right: 1px solid #2A2A2A !important;
  box-shadow: 4px 0 24px rgba(0,0,0,0.50) !important;
}
[data-testid="stSidebar"] > div:first-child {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 20px 16px 20px !important;
  gap: 0;
  background: linear-gradient(180deg, #161616 0%, #0F0F0F 60%, #0A0A0A 100%) !important;
}
[data-testid="stSidebar"] * { font-family: var(--font-sans) !important; }

/* FIX: All sidebar text forced to visible colors */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label {
  color: #C8C8C8 !important;
}

.sb-brand {
  display: flex; align-items: center; gap: 12px;
  padding-bottom: 20px; margin-bottom: 20px;
  border-bottom: 1px solid #2E2E2E;
}
.sb-brand-dot {
  width: 38px; height: 38px; border-radius: 10px;
  background: linear-gradient(135deg, #4B5FD6 0%, #7B8FEE 100%);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0;
  box-shadow: 0 4px 18px rgba(75,95,214,0.50);
}
.sb-brand-text { line-height: 1.2; }
/* FIX: brand name bright white */
.sb-brand-name { font-size: 15px; font-weight: 700; color: #F0F0F0 !important; letter-spacing: -0.2px; }
/* FIX: tag now clearly visible */
.sb-brand-tag  { font-size: 11px; color: #9A9A9A !important; letter-spacing: 0.4px; }

/* FIX: section labels - was #4A4A4A (invisible), now #8A8A8A */
.sb-label {
  font-size: 10.5px; font-weight: 600; color: #8A8A8A !important;
  letter-spacing: 1.4px; text-transform: uppercase; margin-bottom: 8px; padding-left: 2px;
}

[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background: #1C1C1C !important; border: 1.5px solid #3A3A3A !important;
  border-radius: var(--radius-sm) !important; color: #E5E5E5 !important;
  font-size: 13.5px !important; font-weight: 500 !important;
  box-shadow: none !important; transition: border-color 0.2s ease !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover { border-color: #4B5FD6 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] * { color: #E5E5E5 !important; }
[data-testid="stSidebar"] [data-baseweb="popover"] { background: #1C1C1C !important; border: 1px solid #333 !important; }
[data-testid="stSidebar"] [role="option"] { background: #1C1C1C !important; color: #E5E5E5 !important; }
[data-testid="stSidebar"] [role="option"]:hover { background: #2A2A2A !important; }

.sb-spacer { flex: 1 1 auto; }

.sb-stats {
  display: grid; grid-template-columns: 1fr 1fr 1fr;
  gap: 7px; margin-bottom: 16px;
}
.sb-stat-card {
  padding: 11px 8px; background: #1A1A1A;
  border: 1px solid #2E2E2E; border-radius: var(--radius-sm);
  text-align: center; transition: border-color 0.2s;
}
.sb-stat-card:hover { border-color: #3A3A3A; }
/* FIX: stat labels visible */
.sb-stat-label {
  font-size: 9.5px; font-weight: 600; color: #8A8A8A !important;
  letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 5px;
}
/* FIX: stat values bright */
.sb-stat-value { font-size: 19px; font-weight: 700; color: #F0F0F0 !important; line-height: 1; }
.sb-stat-value.warn  { color: #F59E0B !important; }
.sb-stat-value.danger{ color: #EF4444 !important; }

.token-bar-wrap {
  margin-bottom: 16px; padding: 12px 12px 10px;
  background: #1A1A1A; border: 1px solid #2E2E2E; border-radius: var(--radius-sm);
}
.token-bar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px; }
/* FIX: token bar labels visible */
.token-bar-label { font-size: 10px; font-weight: 600; color: #8A8A8A !important; letter-spacing: 1px; text-transform: uppercase; }
.token-bar-pct   { font-size: 11px; font-weight: 700; color: #E0E0E0 !important; }
.token-bar-track { width: 100%; height: 5px; background: #2A2A2A; border-radius: 99px; overflow: hidden; }
.token-bar-fill  { height: 100%; border-radius: 99px; transition: width 0.4s ease; }

.sb-mode-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 10px; background: rgba(75,95,214,0.15);
  border: 1px solid rgba(75,95,214,0.35); border-radius: 20px;
  font-size: 12px; font-weight: 500; color: #9BAAF0 !important;
  margin-bottom: 16px;
}

.stButton > button {
  font-family: var(--font-sans) !important;
  font-size: 13px !important; font-weight: 600 !important;
  padding: 8px 16px !important; border-radius: var(--radius-sm) !important;
  border: 1.5px solid var(--border2) !important;
  background: var(--bg2) !important; color: var(--text2) !important;
  transition: all 0.18s ease !important; box-shadow: var(--shadow-sm) !important;
  cursor: pointer !important;
}
.stButton > button:hover {
  background: var(--bg3) !important; transform: translateY(-1px) !important;
  box-shadow: var(--shadow-md) !important;
}
[data-testid="stSidebar"] .stButton > button {
  background: #1E0A0A !important; border-color: #5C1F1F !important;
  color: #F87171 !important; width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #2D0F0F !important; border-color: #EF4444 !important;
  box-shadow: 0 4px 16px rgba(239,68,68,0.20) !important;
}

/* ── WELCOME ── */
.welcome-wrap {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 52vh; text-align: center; padding: 40px 20px; gap: 0;
}
.welcome-orb {
  width: 88px; height: 88px; border-radius: 50%;
  background: linear-gradient(135deg, #3A4FC8 0%, #6B7FE8 50%, #A78BFA 100%);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 28px;
  box-shadow: 0 8px 32px rgba(75,95,214,0.35), 0 2px 8px rgba(75,95,214,0.20);
  animation: welcome-float 4s ease-in-out infinite;
  position: relative; overflow: hidden;
}
.welcome-orb::after {
  content: ''; position: absolute; inset: 0; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, rgba(255,255,255,0.20) 0%, transparent 60%);
}
@keyframes welcome-float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  33%  { transform: translateY(-8px) rotate(2deg); }
  66%  { transform: translateY(-4px) rotate(-1deg); }
}
.welcome-title {
  font-family: var(--font-serif); font-size: 26px; font-weight: 600;
  color: var(--text1); margin-bottom: 10px; letter-spacing: -0.3px;
}
.welcome-sub { font-size: 14.5px; color: var(--text3); margin-bottom: 32px; line-height: 1.6; }
.chip-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; max-width: 540px; }
.chip {
  padding: 9px 16px; background: var(--bg2); border: 1.5px solid var(--border);
  border-radius: 24px; font-size: 13px; color: var(--text2);
  box-shadow: var(--shadow-sm); cursor: default; transition: all 0.18s ease; font-weight: 450;
}
.chip:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-2px); box-shadow: 0 6px 18px rgba(75,95,214,0.14); }

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
  background: var(--bg2) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important; padding: 18px 22px !important;
  margin-bottom: 12px !important; box-shadow: var(--shadow-sm) !important;
  transition: box-shadow 0.2s ease !important;
}
[data-testid="stChatMessage"]:hover { box-shadow: var(--shadow-md) !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: var(--accent-bg) !important; border-color: var(--accent-bg2) !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
  color: var(--text1) !important; font-family: var(--font-sans) !important;
  font-size: 14.5px !important; line-height: 1.7 !important;
}
[data-testid="stChatMessage"] code {
  background: var(--code-bg) !important; color: var(--accent) !important;
  padding: 2px 7px !important; border-radius: 5px !important;
  font-family: var(--font-mono) !important; font-size: 0.875em !important;
  border: 1px solid var(--border) !important;
}
[data-testid="stChatMessage"] pre {
  background: #1C1917 !important; border-radius: var(--radius-sm) !important;
  padding: 16px 18px !important; margin: 8px 0 !important;
  overflow-x: auto !important; border: 1px solid #292524 !important;
}
[data-testid="stChatMessage"] pre code {
  background: transparent !important; color: #E7E5E4 !important;
  border: none !important; padding: 0 !important; font-size: 13px !important;
}

/* ── ROBOT AVATAR ── */
[data-testid="chatAvatarIcon-assistant"] {
  background: linear-gradient(135deg, #1E2A6E 0%, #3A4FC8 50%, #6B7FE8 100%) !important;
  border: 2px solid rgba(107,127,232,0.40) !important;
  box-shadow: 0 0 14px rgba(75,95,214,0.45), inset 0 1px 0 rgba(255,255,255,0.10) !important;
  border-radius: 50% !important; overflow: hidden !important;
}
[data-testid="chatAvatarIcon-assistant"] svg { display: none !important; }
[data-testid="chatAvatarIcon-assistant"]::after {
  content: ''; display: block; width: 100%; height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 36 36'%3E%3Crect x='8' y='11' width='20' height='14' rx='4' fill='%23E8EEFF'/%3E%3Crect x='13' y='15' width='4' height='4' rx='1.5' fill='%234B5FD6'/%3E%3Crect x='19' y='15' width='4' height='4' rx='1.5' fill='%234B5FD6'/%3E%3Crect x='13' y='21' width='10' height='2' rx='1' fill='%234B5FD6' opacity='.5'/%3E%3Crect x='16' y='7' width='4' height='5' rx='2' fill='%23E8EEFF'/%3E%3Ccircle cx='18' cy='7' r='2' fill='%236B7FE8'/%3E%3Crect x='4' y='14' width='3' height='6' rx='1.5' fill='%23E8EEFF'/%3E%3Crect x='29' y='14' width='3' height='6' rx='1.5' fill='%23E8EEFF'/%3E%3Crect x='13' y='25' width='4' height='3' rx='1' fill='%23E8EEFF'/%3E%3Crect x='19' y='25' width='4' height='3' rx='1' fill='%23E8EEFF'/%3E%3C/svg%3E");
  background-size: 75%; background-repeat: no-repeat; background-position: center;
}

/* ══════════════════════════════════════════
   FIXED IMAGE UPLOADER — always above chat input
   Vision mode mein uploader sticky bottom pe rahega
══════════════════════════════════════════ */
.vision-uploader-fixed {
  position: fixed !important;
  bottom: 78px !important;       /* chat input height ke upar */
  left: 50% !important;
  transform: translateX(-50%) !important;
  width: min(860px, calc(100vw - 290px - 3rem)) !important;
  z-index: 999 !important;
  background: var(--bg) !important;
  padding: 6px 0 2px !important;
}

/* Target the actual Streamlit file uploader when inside vision-uploader-fixed */
.vision-uploader-fixed [data-testid="stFileUploader"] section {
  background: var(--bg2) !important; border: 2px dashed var(--border2) !important;
  border-radius: var(--radius-sm) !important; padding: 10px 14px !important;
  transition: all 0.2s ease !important;
}
.vision-uploader-fixed [data-testid="stFileUploader"] section:hover {
  border-color: var(--accent) !important; background: var(--accent-bg) !important;
}
.vision-uploader-fixed [data-testid="stFileUploader"] small,
.vision-uploader-fixed [data-testid="stFileUploader"] span,
.vision-uploader-fixed [data-testid="stFileUploader"] p { color: var(--text3) !important; font-size: 12px !important; }
.vision-uploader-fixed [data-testid="stFileUploader"] label {
  font-size: 12.5px !important; font-weight: 600 !important; color: var(--text2) !important;
}

/* Fallback: non-fixed uploader (text mode ya fallback) */
[data-testid="stFileUploader"] section {
  background: var(--bg2) !important; border: 2px dashed var(--border2) !important;
  border-radius: var(--radius-sm) !important; padding: 10px 14px !important;
  transition: all 0.2s ease !important;
}
[data-testid="stFileUploader"] section:hover {
  border-color: var(--accent) !important; background: var(--accent-bg) !important;
}
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p { color: var(--text3) !important; font-size: 12px !important; }
[data-testid="stFileUploader"] label {
  font-size: 12.5px !important; font-weight: 600 !important; color: var(--text2) !important;
}

/* ── IMAGE PREVIEW BAR ── */
.img-preview-bar {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 12px;
  background: var(--bg2);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  margin-bottom: 4px;
  box-shadow: var(--shadow-sm);
}
.img-preview-thumb {
  width: 42px; height: 42px; object-fit: cover;
  border-radius: 6px; border: 1px solid var(--border); flex-shrink: 0;
}
.img-preview-name { font-size: 13px; font-weight: 600; color: var(--text1); }
.img-preview-hint { font-size: 11.5px; color: var(--text3); margin-top: 1px; line-height: 1.35; }

/* chat image in message */
.chat-img {
  max-width: 280px; border-radius: var(--radius-sm);
  border: 1px solid var(--border); box-shadow: var(--shadow-sm);
  margin-bottom: 10px; display: block;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] > div {
  background: var(--bg2) !important; border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-md) !important; box-shadow: var(--shadow-md) !important;
  transition: all 0.2s ease !important;
}
[data-testid="stChatInput"] > div:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(75,95,214,0.10), var(--shadow-md) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important; border: none !important;
  color: var(--text1) !important; font-family: var(--font-sans) !important;
  font-size: 14.5px !important; padding: 14px 18px !important;
  caret-color: var(--accent) !important; cursor: text !important;
}
[data-testid="stChatInput"] textarea:focus { outline: none !important; box-shadow: none !important; }
[data-testid="stChatInput"] textarea::placeholder { color: var(--text3) !important; }
[data-testid="stChatInput"] button {
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%) !important;
  border-radius: 10px !important; border: none !important;
  box-shadow: 0 2px 8px rgba(75,95,214,0.30) !important; margin: 6px !important;
}
[data-testid="stChatInput"] button svg { fill: #fff !important; }

/* ── PAGE HEADER ── */
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 18px; margin-bottom: 4px; border-bottom: 1px solid var(--border);
}
.page-header-left { display: flex; align-items: center; gap: 14px; }
.page-header-icon {
  width: 44px; height: 44px; border-radius: 12px;
  background: linear-gradient(135deg, var(--accent) 0%, #7B8FEE 100%);
  display: flex; align-items: center; justify-content: center; font-size: 22px;
  box-shadow: 0 4px 14px rgba(75,95,214,0.28); flex-shrink: 0;
}
.page-header-title {
  font-family: var(--font-serif) !important; font-size: 22px !important;
  font-weight: 600 !important; color: var(--text1) !important;
  letter-spacing: -0.3px; line-height: 1.1;
}
.page-header-sub { font-size: 12.5px !important; color: var(--text3) !important; margin-top: 2px; }

.fallback-notice {
  padding: 10px 14px; background: #FFFBEB; border: 1px solid #FDE68A;
  border-radius: var(--radius-sm); font-size: 12.5px; color: #92400E; margin-bottom: 10px;
}

[data-testid="stSpinner"] p { color: var(--text3) !important; font-size: 13px !important; }
textarea {
  background: var(--bg2) !important; color: var(--text1) !important;
  border: 1.5px solid var(--border) !important; border-radius: var(--radius-sm) !important;
  font-family: var(--font-sans) !important;
}
#MainMenu, footer { visibility: hidden !important; }

@media (max-width: 768px) {
  .main .block-container { padding: 1rem 1rem 200px !important; }
  .page-header-title { font-size: 18px !important; }
  .sb-stats { grid-template-columns: 1fr 1fr !important; }
  .vision-uploader-fixed {
    width: calc(100vw - 2rem) !important;
    left: 1rem !important;
    transform: none !important;
    bottom: 72px !important;
  }
}
</style>
""", unsafe_allow_html=True)

model_mapping = {
    "💬 Text Mode  —  Gemini 2.5 Flash":   "gemini-2.5-flash",
    "🖼️ Vision Mode  —  Gemini 2.0 Flash": "gemini-2.0-flash-lite",
}

TEXT_FALLBACK   = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite"]
VISION_FALLBACK = ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]

def _is_quota_err(e):
    s = str(e); return "429" in s or "ResourceExhausted" in s or "quota" in s.lower()

def _chain(primary, base):
    return [primary] + [m for m in base if m != primary]

for k, v in {
    "messages": [], "last_model": None,
    "uploader_key": 0, "total_tokens": 0,
    "pending_image_b64": None, "pending_pil": None, "pending_name": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
      <div class="sb-brand-dot">🤖</div>
      <div class="sb-brand-text">
        <div class="sb-brand-name">Gen AI Assistant</div>
        <div class="sb-brand-tag">Powered by Gemini</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-label">Model</div>', unsafe_allow_html=True)
    selected_label = st.selectbox(
        "model", list(model_mapping.keys()), index=0, label_visibility="collapsed"
    )
    selected_model = model_mapping[selected_label]
    is_vision = (selected_model == "gemini-2.0-flash-lite")

    if st.session_state.last_model and st.session_state.last_model != selected_model:
        st.session_state.messages = []
        st.session_state.uploader_key += 1
        st.session_state.pending_image_b64 = None
        st.session_state.pending_pil = None
        st.session_state.pending_name = None
    st.session_state.last_model = selected_model

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    mode_icon = "🖼️" if is_vision else "💬"
    mode_text = "Vision + Text" if is_vision else "Text Only"


    msg_count  = len(st.session_state.messages)
    qa_pairs   = msg_count // 2
    tokens_est = st.session_state.total_tokens
    remaining  = max(0, FREE_TOKEN_LIMIT - tokens_est)
    used_pct   = min(100, int(tokens_est / FREE_TOKEN_LIMIT * 100))
    rem_class  = "danger" if used_pct >= 80 else ("warn" if used_pct >= 50 else "")

    def _fmt(n):
        return f"{n/1000:.1f}k" if n >= 1000 else str(n)

    st.markdown(f"""
    <div class="sb-stats">
      <div class="sb-stat-card">
        <div class="sb-stat-label">Chats</div>
        <div class="sb-stat-value">{qa_pairs}</div>
      </div>
      <div class="sb-stat-card">
        <div class="sb-stat-label">Used Token</div>
        <div class="sb-stat-value">{_fmt(tokens_est)}</div>
      </div>
      <div class="sb-stat-card">
        <div class="sb-stat-label">Remaining Token</div>
        <div class="sb-stat-value {rem_class}">{_fmt(remaining)}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    bar_color = "#4B5FD6" if used_pct < 50 else ("#F59E0B" if used_pct < 80 else "#EF4444")
    st.markdown(f"""
    <div class="token-bar-wrap">
      <div class="token-bar-header">
        <span class="token-bar-label">Free Tier Usage</span>
        <span class="token-bar-pct">{used_pct}%</span>
      </div>
      <div class="token-bar-track">
        <div class="token-bar-fill" style="width:{used_pct}%; background:{bar_color};"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.messages:
        if st.button("🗑️  Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.uploader_key += 1
            st.session_state.pending_image_b64 = None
            st.session_state.pending_pil = None
            st.session_state.pending_name = None
            st.rerun()


hcol1, hcol2 = st.columns([6, 1])


with hcol2:
    st.write("")
    if st.session_state.messages:
        if st.button("✕ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.uploader_key += 1
            st.session_state.pending_image_b64 = None
            st.session_state.pending_pil = None
            st.session_state.pending_name = None
            st.rerun()


if not st.session_state.messages:
    chips_text   = ["💡 Explain a complex idea", "✍️ Help me write something", "🧠 Brainstorm ideas", "📚 Summarise text", "🔍 Debug my code", "🌐 Translate this"]
    chips_vision = ["🖼️ Upload image to describe", "🔍 Extract text from photo", "📊 Analyse a chart", "🎨 Critique a design", "📋 Read a document", "🔬 Identify an object"]
    chips = chips_vision if is_vision else chips_text
    chips_html = "".join(f'<span class="chip">{c}</span>' for c in chips)
    st.markdown(f"""
    <div class="welcome-wrap">
      <div class="welcome-orb">🤖</div>
      <div class="welcome-title">How can I help you today?</div>
      <div class="welcome-sub">Ask me anything. I think carefully and answer clearly.</div>
      <div class="chip-grid">{chips_html}</div>
    </div>
    """, unsafe_allow_html=True)


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user" and msg.get("has_image") and msg.get("image_b64"):
            st.markdown(
                f'<img src="data:image/png;base64,{msg["image_b64"]}" class="chat-img" />',
                unsafe_allow_html=True
            )
        st.markdown(msg["content"])


if is_vision:
    st.markdown('<div class="vision-uploader-fixed">', unsafe_allow_html=True)

    if st.session_state.pending_image_b64:
        pil_thumb = st.session_state.pending_pil.copy()
        pil_thumb.thumbnail((60, 60))
        buf_thumb = io.BytesIO()
        pil_thumb.save(buf_thumb, format="PNG")
        b64_thumb = base64.b64encode(buf_thumb.getvalue()).decode()
        st.markdown(f"""
        <div class="img-preview-bar">
          <img src="data:image/png;base64,{b64_thumb}" class="img-preview-thumb" />
          <div>
            <div class="img-preview-name">📎 {st.session_state.pending_name}</div>
            <div class="img-preview-hint">Type a question or press Send to auto-describe.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "📎 Attach image (jpg, png, webp)",
        type=["jpg", "jpeg", "png", "webp"],
        key=f"uploader_{st.session_state.uploader_key}",
        label_visibility="visible",
        help="Upload an image; type a question or press Send to auto-describe."
    )

    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        pil_img = Image.open(io.BytesIO(uploaded_file.getvalue()))
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        if st.session_state.pending_name != uploaded_file.name:
            st.session_state.pending_image_b64 = b64
            st.session_state.pending_pil = pil_img
            st.session_state.pending_name = uploaded_file.name
    else:
        st.session_state.pending_image_b64 = None
        st.session_state.pending_pil = None
        st.session_state.pending_name = None


placeholder_text = (
    "💬 Type a question about the image, or press Send to auto-describe…"
    if (is_vision and st.session_state.pending_image_b64)
    else "💬 Type a message…"
)
user_input = st.chat_input(placeholder_text)


if user_input is not None:
    user_text = user_input.strip()
    has_image = bool(st.session_state.pending_image_b64)
    img_b64   = st.session_state.pending_image_b64
    pil_img   = st.session_state.pending_pil

    if not user_text and has_image:
        user_text = "Please describe this image in detail."

    if not user_text:
        st.stop()

    st.session_state.total_tokens += len(user_text) // 4

    st.session_state.messages.append({
        "role":      "user",
        "content":   user_text,
        "has_image": has_image,
        "image_b64": img_b64,
        "pil_image": pil_img,
    })

    with st.chat_message("user"):
        if has_image and img_b64:
            st.markdown(
                f'<img src="data:image/png;base64,{img_b64}" class="chat-img" />',
                unsafe_allow_html=True
            )
        st.markdown(user_text)

    with st.chat_message("assistant"):
        out_placeholder = st.empty()
        full_response   = ""
        fallback_used   = [None]

        def _stream(prompt, pil_image_arg, chain):
            tried = []
            for i, mname in enumerate(chain):
                try:
                    mdl     = genai.GenerativeModel(mname)
                    content = [prompt, pil_image_arg] if pil_image_arg is not None else prompt
                    resp    = mdl.generate_content(content, stream=True)
                    if i > 0:
                        fallback_used[0] = mname
                    got = False; text_acc = ""
                    for chunk in resp:
                        t = getattr(chunk, "text", None)
                        if t:
                            got = True; text_acc += t
                            yield text_acc
                    if got: return
                    tried.append(mname)
                except Exception as e:
                    tried.append(mname)
                    if _is_quota_err(e) and i < len(chain) - 1: continue
                    if _is_quota_err(e):
                        yield (
                            "**⚠️ All free-tier models are currently rate-limited.**\n\n"
                            f"Tried: `{', '.join(tried)}`\n\nPlease wait ~30 seconds and try again."
                        )
                        return
                    yield f"**❌ Error:** `{str(e)}`"
                    return

        spinner_msg = "Analysing image…" if has_image else "Thinking…"
        with st.spinner(spinner_msg):
            stream_gen = _stream(
                user_text,
                pil_img if (is_vision and has_image) else None,
                _chain(selected_model, VISION_FALLBACK if is_vision else TEXT_FALLBACK)
            )
            for chunk in stream_gen:
                full_response = chunk
                out_placeholder.markdown(full_response + " ▌")

        if fallback_used[0]:
            st.markdown(
                f'<div class="fallback-notice">⚡ Auto-switched to <code>{fallback_used[0]}</code> due to quota limits.</div>',
                unsafe_allow_html=True
            )

        out_placeholder.markdown(full_response)

    st.session_state.total_tokens += len(full_response) // 4

    st.session_state.messages.append({
        "role":      "assistant",
        "content":   full_response,
        "has_image": False,
        "image_b64": None,
    })

    st.session_state.pending_image_b64 = None
    st.session_state.pending_pil = None
    st.session_state.pending_name = None
    st.session_state.uploader_key += 1
    st.rerun()


components.html("""
<script>
const scroll = () => {
  const doc = window.parent.document;
  const main = doc.querySelector('section.main') || doc.querySelector('[data-testid="stMain"]');
  if (main) main.scrollTo({ top: main.scrollHeight, behavior: 'smooth' });
};
setTimeout(scroll, 100);
setTimeout(scroll, 350);
</script>
""", height=0)