import streamlit as st
import requests
import time
import random
import string

# إعدادات الصفحة
st.set_page_config(page_title="Sniper User Roblox", layout="wide")

# CSS بسيط جداً لضمان سرعة التحميل
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #adbac7; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 12px; color: #58a6ff; border-top: 1px solid #30363d; background: #0d1117; }
    .user-box { padding: 5px; border-left: 3px solid #1f6feb; background: #161b22; margin-bottom: 5px; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

# الذاكرة
if "results" not in st.session_state:
    st.session_state.results = {"valid": [], "count": 0}
if "running" not in st.session_state:
    st.session_state.running = False

st.title("🎯 Sniper User Roblox")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Settings")
    u_len = st.number_input("عدد الحروف", 3, 20, 4)
    u_prefix = st.text_input("يبدأ بـ", "")
    use_under = st.checkbox("إجبارية الشرطة _")
    
    if not st.session_state.running:
        if st.button("🚀 ابدأ القنص", use_container_width=True):
            st.session_state.running = True
            st.rerun()
    else:
        if st.button("🛑 إيقاف", use_container_width=True):
            st.session_state.running = False
            st.rerun()

    if st.button("🗑️ مسح", use_container_width=True):
        st.session_state.results = {"valid": [], "count": 0}
        st.rerun()

with col2:
    st.subheader("📊 Results")
    st.write(f"Total Checked: **{st.session_state.results['count']}**")
    st.write(f"Valid Found: **{len(st.session_state.results['valid'])}**")
    
    if st.session_state.results["valid"]:
        st.download_button("📥 تحميل المتاح txt", "\n".join(st.session_state.results["valid"]), "valid.txt")
        for u in reversed(st.session_state.results["valid"][-10:]):
            st.markdown(f'<div class="user-box">{u}</div>', unsafe_allow_html=True)

# المحرك (خفيف جداً)
if st.session_state.running:
    chars = string.ascii_lowercase + string.digits
    for _ in range(5): # يفحص 5 يوزرات في كل دورة
        needed = max(0, u_len - len(u_prefix))
        body = "".join(random.choices(chars, k=needed))
        user = u_prefix + body
        
        if use_under and len(user) > 2:
            l = list(user); l[1] = "_"; user = "".join(l)
            
        try:
            r = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=2)
            if r.status_code == 200 and r.json().get("code") == 0:
                st.session_state.results["valid"].append(user)
        except: pass
        st.session_state.results["count"] += 1
    
    time.sleep(0.1) # تبريد بسيط للسيرفر
    st.rerun()

st.markdown('<div class="footer">Made in Saudi Arabia 🇸🇦 | Dev: 7o.f</div>', unsafe_allow_html=True)
