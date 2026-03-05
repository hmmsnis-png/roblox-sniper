import streamlit as st
import requests
import time
import random
import string

# إعدادات الصفحة - Layout wide للكمبيوتر ويتكيف تلقائياً مع الجوال
st.set_page_config(page_title="Sniper User Roblox", page_icon="🎯", layout="wide")

# تنسيق CSS احترافي وخفيف جداً على المتصفح
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #adbac7; }
    [data-testid="stVerticalBlock"] > div:has(div.element-container) {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 15px;
    }
    .stButton>button {
        width: 100%; border-radius: 8px; background-color: #1f6feb; color: white;
        border: none; font-weight: 600; height: 45px;
    }
    .footer { 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        background-color: #0d1117; color: #58a6ff; 
        padding: 10px 20px; border-top: 1px solid #30363d; 
        font-size: 12px; z-index: 100; display: flex; justify-content: space-between;
    }
    .user-entry { font-family: monospace; padding: 4px; border-left: 3px solid #58a6ff; background: #0d1117; margin-bottom: 2px; font-size: 13px; }
    </style>
    """, unsafe_allow_html=True)

# إدارة البيانات
if "data" not in st.session_state:
    st.session_state.data = {"valid": [], "taken": [], "censored": [], "error": [], "unknown": []}
if "is_running" not in st.session_state:
    st.session_state.is_running = False

st.title("🎯 Sniper User Roblox")

left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("⚙️ Settings")
    is_ar = st.toggle("العربية / English", value=True)
    
    gen_limit = st.slider("Count" if not is_ar else "الكمية", 100, 100000, 1000, 100)
    u_len = st.number_input("Chars" if not is_ar else "عدد الأحرف", 3, 20, 4)
    u_prefix = st.text_input("Prefix" if not is_ar else "يبدأ بـ", placeholder="f5")
    use_under = st.checkbox("Must include '_'" if not is_ar else "إجبارية الشرطة _")

    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start" if not is_ar else "🚀 ابدأ"):
            st.session_state.is_running = True
    with col2:
        if st.button("🛑 Stop" if not is_ar else "🛑 إيقاف"):
            st.session_state.is_running = False

    if st.button("🗑️ Clear" if not is_ar else "🗑️ مسح"):
        st.session_state.data = {k: [] for k in st.session_state.data}
        st.rerun()

    if st.session_state.data["valid"]:
        st.download_button("حفظ المتاح بملف txt", "\n".join(st.session_state.data["valid"]), "valid.txt", use_container_width=True)

with right_col:
    # استخدام Fragment للتحديث الجزيئي (هذا يمنع تعليق الجوال)
    @st.fragment(run_every=1.0) # يحدث الواجهة كل ثانية واحدة فقط لراحة المتصفح
    def show_results():
        total = sum(len(v) for v in st.session_state.data.values())
        m = st.columns(4)
        m[0].metric("TOTAL", total)
        m[1].metric("VALID", len(st.session_state.data["valid"]))
        m[2].metric("TAKEN", len(st.session_state.data["taken"]))
        m[3].metric("CENSORED", len(st.session_state.data["censored"]))

        tabs = st.tabs(["✅ Valid", "❌ Taken", "🚫 Censored", "⚠️ Error", "❓ Unknown"])
        cats = ["valid", "taken", "censored", "error", "unknown"]
        for i, cat in enumerate(cats):
            with tabs[i]:
                for item in reversed(st.session_state.data[cat][-10:]):
                    st.markdown(f'<div class="user-entry">{item}</div>', unsafe_allow_html=True)
    
    show_results()

# محرك الفحص في الخلفية
if st.session_state.is_running:
    chars = string.ascii_lowercase + string.digits
    # فحص دفعة بسيطة ثم إعادة التشغيل لضمان عدم استهلاك موارد الجوال
    for _ in range(5): 
        needed = max(0, u_len - len(u_prefix))
        if use_under and needed > 1:
            body = list(random.choices(chars, k=needed))
            body[random.randint(0, len(body)-1)] = "_"
            user = u_prefix + "".join(body)
            # تصحيح الأطراف
            if user[0] == "_" or user[-1] == "_":
                user = user.replace("_", random.choice(chars))
                if len(user) > 2:
                    l_user = list(user); l_user[1] = "_"; user = "".join(l_user)
        else:
            user = u_prefix + "".join(random.choices(chars, k=needed))

        try:
            r = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=2)
            if r.status_code == 200:
                code = r.json().get("code")
                if code == 0: st.session_state.data["valid"].append(user)
                elif code == 1: st.session_state.data["taken"].append(user)
                elif code == 2: st.session_state.data["censored"].append(user)
                else: st.session_state.data["unknown"].append(user)
            elif r.status_code == 429: time.sleep(1)
        except: pass
    st.rerun()

st.markdown(f"""<div class="footer"><span>Made in Saudi Arabia 🇸🇦</span><span>Developed by: 7o.f</span></div>""", unsafe_allow_html=True)
