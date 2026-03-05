import streamlit as st
import requests
import time
import random
import string
import base64
import os

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Sniper roblox user | 7o.f", page_icon="⚡", layout="wide")

# إدارة الحالة (Session State)
if "data" not in st.session_state: 
    st.session_state.data = {"valid": [], "taken": [], "censored": [], "error": []}
if "is_running" not in st.session_state: 
    st.session_state.is_running = False
if "theme" not in st.session_state: 
    st.session_state.theme = "dark"

# --- 2. التنسيق والسمات (CSS) ---
is_dark = st.session_state.theme == "dark"
bg_color = "#0d1117" if is_dark else "#ffffff"
text_color = "#adbac7" if is_dark else "#1c1e21"
box_bg = "#161b22" if is_dark else "#f0f2f5"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; transition: 0.3s; }}
    [data-testid="stVerticalBlock"] > div:has(div.element-container) {{
        background-color: {box_bg}; border: 1px solid #30363d; border-radius: 12px; padding: 20px;
    }}
    /* خيارات وأزرار روبلوكس باللون الأبيض */
    .stButton>button {{
        width: 100%; border-radius: 8px; font-weight: bold; height: 45px;
        background-color: #ffffff !important; color: #000000 !important; border: 1px solid #cccccc;
    }}
    .user-entry {{
        font-family: monospace; padding: 6px; border-left: 3px solid #58a6ff;
        background: {bg_color}; margin-bottom: 3px; color: {text_color};
    }}
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%; background: {bg_color};
        padding: 10px; text-align: center; border-top: 1px solid #30363d; color: #58a6ff; z-index: 100;
    }}
    </style>
    """, unsafe_allow_html=True)

# دالة لعرض الشعار (معدلة للبحث عن الاسم الجديد وتجنب الخطأ)
def get_base64_img(file_name):
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# جلب الصورة باسمها الجديد
img_data = get_base64_img("robloxbiru2.png")

# تصميم الهيدر (شعار + اسم)
if img_data:
    logo_html = f'<img src="data:image/png;base64,{img_data}" width="60">'
else:
    # أيقونة بديلة في حال عدم وجود الصورة
    logo_html = '<div style="background:#58a6ff; width:50px; height:50px; border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:24px;">R</div>'

# --- 3. الواجهة الرئيسية ---
st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        {logo_html}
        <h1 style="color: {text_color}; margin: 0;">Sniper roblox user</h1>
    </div>
    """, unsafe_allow_html=True)

left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    # إعدادات اللغة والسمة
    is_ar = st.radio("Language / اللغة", ["العربية", "English"], horizontal=True, label_visibility="collapsed") == "العربية"
    
    # زر تغيير السمة مع ترجمة متغيرة
    theme_btn_text = ("تغيير لون الصفحة (أبيض/أسود)" if is_ar else "Toggle Page Color (Light/Dark)")
    if st.button(theme_btn_text):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()

    st.subheader("⚙️ " + ("الإعدادات" if is_ar else "Settings"))
    
    gen_limit = st.slider("الكمية" if is_ar else "Count", 100, 100000, 5000, 100)
    u_len = st.number_input("طول اليوزر" if is_ar else "Username Length", 3, 20, 4)
    
    u_prefix = st.text_input("يبدأ اليوزر بـ" if is_ar else "User Starts With", value="")
    u_suffix = st.text_input("ينتهي اليوزر بـ" if is_ar else "User Ends With", value="")
    
    speed_option = st.select_slider(
        "سرعة الفحص" if is_ar else "Scanning Speed",
        options=["Slow", "Normal", "Fast", "Extreme"], value="Fast"
    )
    delay_map = {"Slow": 0.8, "Normal": 0.5, "Fast": 0.2, "Extreme": 0.1}
    current_delay = delay_map[speed_option]
    
    use_under = st.checkbox("إضافة شرطة _" if is_ar else "Add Underscore _")

    st.divider()
    
    if not st.session_state.is_running:
        if st.button("🚀 " + ("ابدأ" if is_ar else "Start"), type="primary"):
            st.session_state.is_running = True
            st.rerun()
    else:
        if st.button("🛑 " + ("إيقاف" if is_ar else "Stop"), type="primary"):
            st.session_state.is_running = False
            st.rerun()

    if st.button("🗑️ " + ("مسح" if is_ar else "Clear")):
        st.session_state.data = {k: [] for k in st.session_state.data}
        st.rerun()

with right_col:
    d = st.session_state.data
    total = sum(len(v) for v in d.values())
    
    m = st.columns(4)
    m[0].metric("TOTAL", total)
    m[1].metric("VALID", len(d["valid"]))
    m[2].metric("TAKEN", len(d["taken"]))
    m[3].metric("BAN", len(d["censored"]))

    tabs = st.tabs(["✅ متاح", "❌ مستخدم", "🚫 مبند", "⚠️ أخطاء"] if is_ar else ["✅ Valid", "❌ Taken", "🚫 Ban", "⚠️ Errors"])
    categories = ["valid", "taken", "censored", "error"]
    
    for i, cat in enumerate(categories):
        with tabs[i]:
            for item in reversed(d[cat][-12:]):
                st.markdown(f'<div class="user-entry">{item}</div>', unsafe_allow_html=True)

# --- 4. محرك الفحص ---
if st.session_state.is_running:
    needed = max(1, u_len - len(u_prefix) - len(u_suffix))
    body = "".join(random.choices(string.ascii_lowercase + string.digits, k=needed))
    user = u_prefix + body + u_suffix
    
    if use_under and len(user) > 2:
        l_u = list(user); idx = random.randint(1, len(l_u) - 2)
        l_u[idx] = "_"; user = "".join(l_u)

    try:
        r = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=0.5)
        if r.status_code == 200:
            code = r.json().get("code")
            if code == 0: st.session_state.data["valid"].append(user)
            elif code == 1: st.session_state.data["taken"].append(user)
            elif code == 2: st.session_state.data["censored"].append(user)
        elif r.status_code == 429:
            time.sleep(3)
    except:
        pass
    
    time.sleep(current_delay)
    st.rerun()

st.markdown(f"""
    <div class="footer">
        Developed by: 7o.f | discord: 7o.f | Mode: {speed_option}<br>
        Made in Saudi Arabia 🇸🇦
    </div>
""", unsafe_allow_html=True)
