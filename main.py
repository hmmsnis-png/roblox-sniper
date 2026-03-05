import streamlit as st
import requests
import time
import random
import string

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(page_title="Sniper User Roblox | 7o.f", page_icon="🎯", layout="wide")

# --- 2. التنسيق (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #adbac7; }
    [data-testid="stVerticalBlock"] > div:has(div.element-container) {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px;
    }
    .stButton>button {
        width: 100%; border-radius: 8px; background-color: #1f6feb; color: white;
        border: none; font-weight: 600; height: 45px;
    }
    .stButton>button:hover { background-color: #388bfd; }
    .footer { 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        background-color: #0d1117; color: #58a6ff; 
        padding: 10px 25px; border-top: 1px solid #30363d; 
        font-size: 14px; z-index: 100; display: flex; justify-content: space-between;
    }
    .user-entry { 
        font-family: 'Source Code Pro', monospace; padding: 6px; 
        border-radius: 4px; margin-bottom: 4px; border-left: 3px solid #58a6ff; 
        background: #0d1117; color: #e6edf3;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. إدارة البيانات (Session State) ---
if "data" not in st.session_state:
    st.session_state.data = {"valid": [], "taken": [], "censored": [], "error": [], "unknown": []}
if "is_running" not in st.session_state: 
    st.session_state.is_running = False

# --- 4. الواجهة الجانبية (Settings) ---
st.title("🎯 Sniper User Roblox")

left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.subheader("⚙️ Settings")
    lang = st.radio("Language", ["English", "العربية"], horizontal=True, label_visibility="collapsed")
    is_ar = lang == "العربية"
    
    gen_limit = st.slider("Count" if not is_ar else "الكمية", 100, 100000, 1000, 100)
    u_len = st.number_input("Chars" if not is_ar else "عدد الأحرف", 3, 20, 4)
    u_prefix = st.text_input("Prefix" if not is_ar else "يبدأ بـ", placeholder="f5")
    use_under = st.checkbox("Must include '_'" if not is_ar else "إجبارية الشرطة _")

    st.divider()
    
    # أزرار التحكم
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🚀 Start" if not is_ar else "🚀 ابدأ"):
            st.session_state.is_running = True
    with col_btn2:
        if st.button("🛑 Stop" if not is_ar else "🛑 إيقاف"):
            st.session_state.is_running = False

    if st.button("🗑️ Clear" if not is_ar else "🗑️ مسح"):
        st.session_state.data = {k: [] for k in st.session_state.data}
        st.rerun()

    # زر التحميل
    if st.session_state.data["valid"]:
        valid_text = "\n".join(st.session_state.data["valid"])
        st.download_button("حفظ اليوزرات المتاحة بملف txt", valid_text, "valid.txt", use_container_width=True)

# --- 5. منطقة النتائج (تحديث سلس) ---
with right_col:
    total_found = sum(len(v) for v in st.session_state.data.values())
    
    # الإحصائيات
    m_cols = st.columns(4)
    m_cols[0].metric("TOTAL", total_found)
    m_cols[1].metric("VALID", len(st.session_state.data["valid"]))
    m_cols[2].metric("TAKEN", len(st.session_state.data["taken"]))
    m_cols[3].metric("CENSORED", len(st.session_state.data["censored"]))

    tabs = st.tabs(["✅ Valid", "❌ Taken", "🚫 Censored", "⚠️ Errors", "❓ Unknown"] if not is_ar 
                   else ["✅ متاح", "❌ مستخدم", "🚫 مبند", "⚠️ أخطاء", "❓ غير معروف"])
    
    # عرض النتائج في التبويبات
    categories = ["valid", "taken", "censored", "error", "unknown"]
    for i, cat in enumerate(categories):
        with tabs[i]:
            for item in reversed(st.session_state.data[cat][-15:]):
                st.markdown(f'<div class="user-entry">{item}</div>', unsafe_allow_html=True)

# --- 6. المحرك (Engine) ---
# نستخدم rerun في نهاية الفحص لضمان تحديث الأرقام واحد بواحد بسلاسة
if st.session_state.is_running and total_found < gen_limit:
    chars = string.ascii_lowercase + string.digits
    
    # توليد اليوزر
    needed = max(0, u_len - len(u_prefix))
    if use_under and needed > 1:
        body = list(random.choices(chars, k=needed))
        idx = random.randint(0, len(body)-1)
        body[idx] = "_"
        user = u_prefix + "".join(body)
        # تصحيح الأطراف
        if user.startswith("_") or user.endswith("_"):
            user_list = list(user)
            if user_list[0] == "_": user_list[0] = random.choice(chars)
            if user_list[-1] == "_": user_list[-1] = random.choice(chars)
            mid = random.randint(1, len(user_list)-2)
            user_list[mid] = "_"
            user = "".join(user_list)
    else:
        user = u_prefix + "".join(random.choices(chars, k=needed))

    # فحص اليوزر
    try:
        r = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=3)
        if r.status_code == 200:
            code = r.json().get("code")
            if code == 0: st.session_state.data["valid"].append(user)
            elif code == 1: st.session_state.data["taken"].append(user)
            elif code == 2: st.session_state.data["censored"].append(user)
            else: st.session_state.data["unknown"].append(user)
        elif r.status_code == 429:
            time.sleep(1)
    except:
        pass

    # هذه الحركة هي اللي تخلي الموقع يفتح فوراً وتحدث الأرقام بسلاسة
    st.rerun()

# --- 7. الفوتر ---
st.markdown(f"""
    <div class="footer">
        <span>Made in Saudi Arabia 🇸🇦</span>
        <span>Developed by: 7o.f | Discord: 7o.f</span>
    </div>
    """, unsafe_allow_html=True)
