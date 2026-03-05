import streamlit as st
import requests
import time
import random
import string

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Custom Speed Sniper | 7o.f", page_icon="⚙️", layout="wide")

# --- 2. التنسيق (CSS) ---
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

if "data" not in st.session_state:
    st.session_state.data = {"valid": [], "taken": [], "censored": [], "error": [], "unknown": []}
if "is_running" not in st.session_state: st.session_state.is_running = False

st.title("🚀 Sniper User Roblox (Custom Speed)")

left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.subheader("⚙️ الإعدادات / Settings")
    is_ar = st.radio("Language", ["العربية", "English"], horizontal=True, label_visibility="collapsed") == "العربية"
    
    gen_limit = st.slider("الكمية" if is_ar else "Count", 100, 100000, 5000, 100)
    u_len = st.number_input("Username Length" if not is_ar else "عدد أحرف اليوزر", 3, 20, 4)
    u_prefix = st.text_input("يبدأ اليوزر بـ" if is_ar else "User Starts With", value="")
    
    # --- التعديل الجديد: خيار سرعة الفحص ---
    st.markdown(f"**{'سرعة الفحص' if is_ar else 'Scanning Speed'}**")
    speed_option = st.select_slider(
        "Speed",
        options=["Normal", "Fast", "Ultra Fast", "Extreme"],
        value="Fast",
        label_visibility="collapsed"
    )
    
    # تحديد عدد الفحوصات بناءً على السرعة المختارة
    speed_map = {"Normal": 5, "Fast": 20, "Ultra Fast": 50, "Extreme": 100}
    batch_size = speed_map[speed_option]
    
    use_under = st.checkbox("ضع شرطة باليوزر _" if is_ar else "Add Underscore _")
    use_numbers = st.checkbox("إضافة أرقام باليوزر" if is_ar else "Add numbers", value=True)

    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 ابدأ" if is_ar else "🚀 Start"):
            st.session_state.is_running = True
            st.rerun()
    with c2:
        if st.button("🛑 إيقاف" if is_ar else "🛑 Stop"):
            st.session_state.is_running = False
            st.rerun()

    if st.button("🗑️ مسح" if is_ar else "🗑️ Clear"):
        st.session_state.data = {k: [] for k in st.session_state.data}
        st.rerun()

    if st.session_state.data["valid"]:
        st.download_button("📥 حفظ المتاح txt", "\n".join(st.session_state.data["valid"]), "valid.txt", use_container_width=True)

with right_col:
    total_found = sum(len(v) for v in st.session_state.data.values())
    m = st.columns(4)
    m[0].metric("TOTAL", total_found)
    m[1].metric("VALID", len(st.session_state.data["valid"]))
    m[2].metric("TAKEN", len(st.session_state.data["taken"]))
    m[3].metric("CENSORED", len(st.session_state.data["censored"]))

    tabs = st.tabs(["✅ متاح", "❌ مستخدم", "🚫 مبند", "⚠️ أخطاء", "❓ غير معروف"] if is_ar else ["✅ Valid", "❌ Taken", "🚫 Censored", "⚠️ Errors", "❓ Unknown"])
    cats = ["valid", "taken", "censored", "error", "unknown"]
    for i, cat in enumerate(cats):
        with tabs[i]:
            for item in reversed(st.session_state.data[cat][-15:]):
                st.markdown(f'<div class="user-entry">{item}</div>', unsafe_allow_html=True)

# --- المحرك المعتمد على السرعة ---
if st.session_state.is_running and total_found < gen_limit:
    chars = (string.ascii_lowercase + string.digits) if use_numbers else string.ascii_lowercase
    
    # الفحص يعتمد على القيمة المختارة من المنزلق (batch_size)
    for _ in range(batch_size):
        needed = max(0, u_len - len(u_prefix))
        body = "".join(random.choices(chars, k=needed))
        user = u_prefix + body
        
        if use_under and len(user) > 2:
            l_u = list(user)
            idx = random.randint(1, len(l_u) - 2)
            l_u[idx] = "_"
            user = "".join(l_u)

        try:
            # تقليل وقت الانتظار لزيادة الفاعلية في السرعات العالية
            r = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=0.8)
            if r.status_code == 200:
                code = r.json().get("code")
                if code == 0: st.session_state.data["valid"].append(user)
                elif code == 1: st.session_state.data["taken"].append(user)
                elif code == 2: st.session_state.data["censored"].append(user)
                else: st.session_state.data["unknown"].append(user)
            elif r.status_code == 429:
                time.sleep(1)
                break
        except:
            pass
    
    st.rerun()

st.markdown(f"""<div class="footer">Developed by: 7o.f | Mode: {speed_option} 🇸🇦</div>""", unsafe_allow_html=True)
