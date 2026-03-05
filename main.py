import streamlit as st
import requests
import time
import random
import string

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Sniper roblox user | 7o.f", layout="wide")

# --- 2. التنسيق (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #adbac7; }
    [data-testid="stVerticalBlock"] > div:has(div.element-container) {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px;
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; height: 45px; }
    .user-entry { font-family: monospace; padding: 4px; border-left: 3px solid #58a6ff; background: #0d1117; margin-bottom: 2px; font-size: 13px; }
    .footer { 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        background: #0d1117; padding: 10px; text-align: center; 
        border-top: 1px solid #30363d; color: #58a6ff; z-index: 100;
    }
    .made-in { font-weight: bold; margin-top: 5px; color: #adbac7; }
    </style>
    """, unsafe_allow_html=True)

if "data" not in st.session_state:
    st.session_state.data = {"valid": [], "taken": [], "censored": [], "error": [], "unknown": []}
if "is_running" not in st.session_state: 
    st.session_state.is_running = False
    
img_data = get_base64_img("783289-robloxbiru2.png")

st.title("Sniper roblox user")

left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.subheader("⚙️ Settings")
    is_ar = st.radio("Language", ["العربية", "English"], horizontal=True, label_visibility="collapsed") == "العربية"
    
    gen_limit = st.slider("الكمية" if is_ar else "Count", 100, 100000, 5000, 100)
    u_len = st.number_input("Username Length" if not is_ar else "عدد أحرف اليوزر", 3, 20, 4)
    u_prefix = st.text_input("يبدأ اليوزر بـ" if is_ar else "User Starts With", value="")
    
    speed_option = st.select_slider(
        "Scanning Speed" if not is_ar else "سرعة الفحص",
        options=["Slow", "Normal", "Fast", "Extreme"],
        value="Extreme"
    )
    
    # السرعة القصوى (أقل تأخير ممكن)
    delay_map = {"Slow": 0.8, "Normal": 0.5, "Fast": 0.3, "Extreme": 0.1}
    current_delay = delay_map[speed_option]
    
    use_under = st.checkbox("ضع شرطة باليوزر _" if is_ar else "Add Underscore _")
    use_numbers = st.checkbox("إضافة أرقام باليوزر" if is_ar else "Add numbers", value=True)

    st.divider()
    
    if not st.session_state.is_running:
        if st.button("🚀 " + ("ابدأ" if is_ar else "Start"), type="primary"):
            st.session_state.is_running = True
            st.rerun()
    else:
        if st.button("🛑 " + ("إيقاف" if is_ar else "Stop"), type="secondary"):
            st.session_state.is_running = False
            st.rerun()

    if st.button("🗑️ " + ("مسح" if is_ar else "Clear")):
        st.session_state.data = {k: [] for k in st.session_state.data}
        st.rerun()

    if st.session_state.data["valid"]:
        st.download_button(
            label="📥 " + ("حفظ المتاح" if is_ar else "Save Valid"),
            data="\n".join(st.session_state.data["valid"]),
            file_name="users.txt",
            mime="text/plain",
            use_container_width=True
        )

with right_col:
    stats_placeholder = st.empty()
    tabs_placeholder = st.empty()

def update_ui():
    with stats_placeholder:
        total = sum(len(v) for v in st.session_state.data.values())
        m = st.columns(4)
        m[0].metric("TOTAL", total)
        m[1].metric("VALID", len(st.session_state.data["valid"]))
        m[2].metric("TAKEN", len(st.session_state.data["taken"]))
        m[3].metric("CENSORED", len(st.session_state.data["censored"]))
    
    with tabs_placeholder:
        tabs = st.tabs(["✅ متاح", "❌ مستخدم", "🚫 مبند", "⚠️ أخطاء", "❓ غير معروف"] if is_ar else ["✅ Valid", "❌ Taken", "🚫 Censored", "⚠️ Errors", "❓ Unknown"])
        cats = ["valid", "taken", "censored", "error", "unknown"]
        for i, cat in enumerate(cats):
            with tabs[i]:
                for item in reversed(st.session_state.data[cat][-12:]):
                    st.markdown(f'<div class="user-entry">{item}</div>', unsafe_allow_html=True)

update_ui()

if st.session_state.is_running:
    chars = (string.ascii_lowercase + string.digits) if use_numbers else string.ascii_lowercase
    while st.session_state.is_running:
        total_found = sum(len(v) for v in st.session_state.data.values())
        if total_found >= gen_limit:
            st.session_state.is_running = False; st.rerun(); break
            
        needed = max(0, u_len - len(u_prefix))
        body = "".join(random.choices(chars, k=needed))
        user = u_prefix + body
        
        if use_under and len(user) > 2:
            l_u = list(user); idx = random.randint(1, len(l_u) - 2)
            l_u[idx] = "_"; user = "".join(l_u)

        try:
            r = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=0.8)
            if r.status_code == 200:
                code = r.json().get("code")
                if code == 0: st.session_state.data["valid"].append(user)
                elif code == 1: st.session_state.data["taken"].append(user)
                elif code == 2: st.session_state.data["censored"].append(user)
                else: st.session_state.data["unknown"].append(user)
            elif r.status_code == 429:
                time.sleep(3)
        except: pass
        
        update_ui()
        if current_delay > 0: time.sleep(current_delay)

# الفوتر المعدل - السطر الأول حقوق، السطر الثاني السعودية
st.markdown(f"""
    <div class="footer">
        <div>Developed by: 7o.f | discord: 7o.f | Mode: {speed_option}</div>
        <div class="made-in">Made in Saudi Arabia 🇸🇦</div>
    </div>
""", unsafe_allow_html=True)


