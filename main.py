import streamlit as st
import requests
import time
import random
import string
import base64
import os

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Sniper roblox user | 7o.f", layout="wide")

# إدارة الحالة
if "data" not in st.session_state: 
    st.session_state.data = {"valid": [], "taken": [], "censored": [], "error": []}
if "is_running" not in st.session_state: st.session_state.is_running = False
if "theme" not in st.session_state: st.session_state.theme = "dark"

# --- 2. التنسيق والسمات (CSS) ---
is_dark = st.session_state.theme == "dark"
bg_color = "#000000" if is_dark else "#ffffff"
text_color = "#ffffff" if is_dark else "#000000"
blue_main = "#007bff" # اللون الأزرق المطلوب

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; transition: 0.3s; }}
    
    /* جعل كل الحقول والخيارات باللون الأزرق */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {{
        border: 2px solid {blue_main} !important;
        color: {text_color} !important;
        background-color: transparent !important;
    }}
    
    /* الأزرار زرقاء دائماً */
    .stButton>button {{
        width: 100%; border-radius: 8px; font-weight: bold; height: 45px;
        background-color: {blue_main} !important; color: white !important; border: none;
    }}

    /* تنسيق مستطيلات الإحصائيات زرقاء */
    [data-testid="stMetric"] {{
        background-color: transparent;
        border: 2px solid {blue_main};
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }}
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
        color: {blue_main} !important;
    }}

    .user-entry {{
        font-family: monospace; padding: 6px; border-left: 3px solid {blue_main};
        background: rgba(0, 123, 255, 0.1); margin-bottom: 3px; color: {text_color};
    }}
    
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%; background: {bg_color};
        padding: 10px; text-align: center; border-top: 1px solid {blue_main}; color: {blue_main}; z-index: 100;
    }}
    </style>
    """, unsafe_allow_html=True)

def get_base64_img(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

img_data = get_base64_img("robloxbiru2.png")

# --- 3. الواجهة الرئيسية ---
logo_html = f'<img src="data:image/png;base64,{img_data}" width="60">' if img_data else '<span style="font-size:40px;">🟦</span>'

st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        {logo_html}
        <h1 style="color: {blue_main}; margin: 0;">Sniper roblox user</h1>
    </div>
    """, unsafe_allow_html=True)

left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    is_ar = st.radio("Language", ["العربية", "English"], horizontal=True, label_visibility="collapsed") == "العربية"
    
    theme_btn = "تغيير اللون (أبيض/أسود)" if is_ar else "Toggle Color (Light/Dark)"
    if st.button(theme_btn):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()

    st.subheader("⚙️ Settings")
    u_len = st.number_input("Username Length", 3, 20, 4)
    u_prefix = st.text_input("User Starts With", value="")
    u_suffix = st.text_input("User Ends With", value="")
    
    # خيار الأرقام (مفعل تلقائياً)
    use_numbers = st.checkbox("Add Numbers / إضافة أرقام", value=True)
    use_under = st.checkbox("Add Underscore / إضافة شرطة _", value=False)
    
    speed_option = st.select_slider("Speed", options=["Slow", "Normal", "Fast", "Extreme"], value="Fast")
    delay = {"Slow": 0.8, "Normal": 0.5, "Fast": 0.2, "Extreme": 0.1}[speed_option]

    if not st.session_state.is_running:
        if st.button("🚀 START", type="primary"): st.session_state.is_running = True; st.rerun()
    else:
        if st.button("🛑 STOP", type="primary"): st.session_state.is_running = False; st.rerun()

    if st.button("🗑️ CLEAR"):
        st.session_state.data = {k: [] for k in st.session_state.data}; st.rerun()

with right_col:
    d = st.session_state.data
    m = st.columns(4)
    # الإحصائيات مع كلمة censored بدلاً من BAN
    m[0].metric("TOTAL", sum(len(v) for v in d.values()))
    m[1].metric("VALID", len(d["valid"]))
    m[2].metric("TAKEN", len(d["taken"]))
    m[3].metric("CENSORED", len(d["censored"]))

    tabs = st.tabs(["✅ Valid", "❌ Taken", "🚫 Censored", "⚠️ Errors"])
    cats = ["valid", "taken", "censored", "error"]
    for i, cat in enumerate(cats):
        with tabs[i]:
            for item in reversed(d[cat][-12:]):
                st.markdown(f'<div class="user-entry">{item}</div>', unsafe_allow_html=True)

# --- 4. محرك الفحص ---
if st.session_state.is_running:
    chars = string.ascii_lowercase
    if use_numbers: chars += string.digits
    
    needed = max(1, u_len - len(u_prefix) - len(u_suffix))
    body = "".join(random.choices(chars, k=needed))
    user = u_prefix + body + u_suffix
    
    if use_under and len(user) > 2:
        l_u = list(user); l_u[random.randint(1, len(l_u)-2)] = "_"; user = "".join(l_u)

    try:
        r = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=0.5)
        if r.status_code == 200:
            code = r.json().get("code")
            if code == 0: st.session_state.data["valid"].append(user)
            elif code == 1: st.session_state.data["taken"].append(user)
            elif code == 2: st.session_state.data["censored"].append(user)
    except: pass
    time.sleep(delay); st.rerun()

st.markdown(f'<div class="footer">Developed by: 7o.f | discord: 7o.f | Made in Saudi Arabia 🇸🇦</div>', unsafe_allow_html=True)
