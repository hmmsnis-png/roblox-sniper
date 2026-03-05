import streamlit as st
import requests
import time
import random
import string

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Sniper Roblox | 7o.f", page_icon="🎯", layout="wide")

# --- 2. التنسيق (CSS) لضمان عدم اهتزاز الشاشة ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #adbac7; }
    [data-testid="stVerticalBlock"] > div:has(div.element-container) {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px;
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; height: 45px; }
    .user-entry { font-family: monospace; padding: 4px; border-left: 3px solid #58a6ff; background: #0d1117; margin-bottom: 2px; font-size: 13px; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background: #0d1117; padding: 10px; text-align: center; border-top: 1px solid #30363d; color: #58a6ff; z-index: 100; }
    </style>
    """, unsafe_allow_html=True)

# إدارة الحالة (Session State)
if "data" not in st.session_state:
    st.session_state.data = {"valid": [], "taken": [], "censored": [], "error": [], "unknown": []}
if "is_running" not in st.session_state: 
    st.session_state.is_running = False

st.title("🎯 Sniper User Roblox")

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
        value="Normal"
    )
    
    delay_map = {"Slow": 0.8, "Normal": 0.4, "Fast": 0.1, "Extreme": 0.01}
    current_delay = delay_map[speed_option]
    
    use_under = st.checkbox("ضع شرطة باليوزر _" if is_ar else "Add Underscore _")
    use_numbers = st.checkbox("إضافة أرقام باليوزر" if is_ar else "Add numbers", value=True)

    st.divider()
    
    # الزر الديناميكي (بدء / إيقاف)
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

    download_placeholder = st.empty()
    if st.session_state.data["valid"]:
        download_placeholder.download_button("📥 " + ("حفظ المتاح" if is_ar else "Save Valid"), "\n".join(st.session_state.data["valid"]), "valid.txt", use_container_width=True)

with right_col:
    # استخدام containers لتحديث الأرقام بدون إعادة تحميل الصفحة
    stats_container = st.empty()
    tabs_container = st.empty()

# دالة لتحديث عرض النتائج
def update_display():
    with stats_container:
        total = sum(len(v) for v in st.session_state.data.values())
        m = st.columns(4)
        m[0].metric("TOTAL", total)
        m[1].metric("VALID", len(st.session_state.data["valid"]))
        m[2].metric("TAKEN", len(st.session_state.data["taken"]))
        m[3].metric("CENSORED", len(st.session_state.data["censored"]))
    
    with tabs_container:
        tabs = st.tabs(["✅ متاح", "❌ مستخدم", "🚫 مبند", "⚠️ أخطاء", "❓ غير معروف"] if is_ar else ["✅ Valid", "❌ Taken", "🚫 Censored", "⚠️ Errors", "❓ Unknown"])
        cats = ["valid", "taken", "censored", "error", "unknown"]
        for i, cat in enumerate(cats):
            with tabs[i]:
                # عرض آخر 10 نتائج فقط لسرعة الأداء
                for item in reversed(st.session_state.data[cat][-10:]):
                    st.markdown(f'<div class="user-entry">{item}</div>', unsafe_allow_html=True)

# تشغيل العرض الأولي
update_display()

# --- محرك القنص (العمل في حلقة داخلية لتجنب الشاشة البيضاء) ---
if st.session_state.is_running:
    chars = (string.ascii_lowercase + string.digits) if use_numbers else string.ascii_lowercase
    
    while st.session_state.is_running:
        total_found = sum(len(v) for v in st.session_state.data.values())
        if total_found >= gen_limit:
            st.session_state.is_running = False
            st.rerun()
            break
            
        needed = max(0, u_len - len(u_prefix))
        body = "".join(random.choices(chars, k=needed))
        user = u_prefix + body
        
        if use_under and len(user) > 2:
            l_u = list(user); idx = random.randint(1, len(l_u) - 2)
            l_u[idx] = "_"; user = "".join(l_u)

        try:
            r = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=1.5)
            if r.status_code == 200:
                code = r.json().get("code")
                if code == 0: st.session_state.data["valid"].append(user)
                elif code == 1: st.session_state.data["taken"].append(user)
                elif code == 2: st.session_state.data["censored"].append(user)
                else: st.session_state.data["unknown"].append(user)
            elif r.status_code == 429:
                time.sleep(5) # حظر مؤقت من روبلوكس
        except:
            pass
        
        # تحديث الواجهة فوراً بدون Rerun للموقع كامل
        update_display()
        
        if current_delay > 0:
            time.sleep(current_delay)

st.markdown(f"""<div class="footer">Developed by: 7o.f | Mode: {speed_option} 🇸🇦</div>""", unsafe_allow_html=True)
