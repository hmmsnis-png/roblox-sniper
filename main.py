import streamlit as st
import requests
import time
import random
import string

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Sniper User Roblox", layout="wide")

# --- التنسيق (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #adbac7; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 12px; color: #58a6ff; border-top: 1px solid #30363d; background: #0d1117; }
    .user-box { padding: 5px; border-left: 3px solid #1f6feb; background: #161b22; margin-bottom: 5px; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

# إدارة البيانات
if "results" not in st.session_state:
    st.session_state.results = {"valid": [], "count": 0}
if "running" not in st.session_state:
    st.session_state.running = False

st.title("🎯 Sniper User Roblox")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Settings / الإعدادات")
    
    # التعديلات المطلوبة هنا
    u_len = st.number_input("عدد أحرف اليوزر", 3, 20, 4)
    u_prefix = st.text_input("بداية اليوزر بـ", value="") # الحقل الآن فارغ تماماً
    use_under = st.checkbox("شرطة باليوزر _") # تغيير المسمى
    
    st.markdown("---")
    
    if not st.session_state.running:
        if st.button("🚀 ابدأ القنص", use_container_width=True):
            st.session_state.running = True
            st.rerun()
    else:
        if st.button("🛑 إيقاف", use_container_width=True):
            st.session_state.running = False
            st.rerun()

    if st.button("🗑️ مسح النتائج", use_container_width=True):
        st.session_state.results = {"valid": [], "count": 0}
        st.rerun()

    if st.session_state.results["valid"]:
        st.download_button("حفظ اليوزرات المتاحة بملف txt", 
                           "\n".join(st.session_state.results["valid"]), 
                           "valid.txt", use_container_width=True)

with col2:
    st.subheader("📊 النتائج الحالية")
    st.write(f"اليوزرات المفحوصة: **{st.session_state.results['count']}**")
    st.write(f"اليوزرات المتاحة: **{len(st.session_state.results['valid'])}**")
    
    if st.session_state.results["valid"]:
        for u in reversed(st.session_state.results["valid"][-15:]):
            st.markdown(f'<div class="user-box">{u}</div>', unsafe_allow_html=True)

# --- المحرك (Engine) ---
if st.session_state.running:
    chars = string.ascii_lowercase + string.digits
    for _ in range(5):
        needed = max(0, u_len - len(u_prefix))
        body = "".join(random.choices(chars, k=needed))
        user = u_prefix + body
        
        # منطق الشرطة الإجباري إذا تم تفعيله
        if use_under and len(user) > 2:
            l_user = list(user)
            # وضع الشرطة في مكان عشوائي ليس في الأطراف
            idx = random.randint(1, len(l_user) - 2)
            l_user[idx] = "_"
            user = "".join(l_user)
            
        try:
            r = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=2)
            if r.status_code == 200 and r.json().get("code") == 0:
                st.session_state.results["valid"].append(user)
        except:
            pass
        st.session_state.results["count"] += 1
    
    time.sleep(0.1)
    st.rerun()

st.markdown('<div class="footer">Made in Saudi Arabia 🇸🇦 | Developed by: 7o.f</div>', unsafe_allow_html=True)
