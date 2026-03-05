import streamlit as st
import requests
import time
import random
import string

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Sniper User Roblox | 7o.f", page_icon="🎯", layout="wide")

# --- تنسيق CSS المطور ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #adbac7; }
    [data-testid="stVerticalBlock"] > div:has(div.element-container) {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px;
    }
    .stButton>button {
        width: 100%; border-radius: 8px; background-color: #1f6feb; color: white;
        border: none; transition: 0.3s; font-weight: 600; height: 45px;
    }
    .stButton>button:hover { background-color: #388bfd; transform: translateY(-2px); }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Inter', sans-serif; }
    
    /* الفوتر المطور بجهتين */
    .footer { 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        background-color: #0d1117; color: #58a6ff; 
        padding: 10px 25px; border-top: 1px solid #30363d; 
        font-size: 14px; z-index: 100;
        display: flex; justify-content: space-between;
    }
    
    .user-entry { 
        font-family: 'Source Code Pro', monospace; padding: 6px 12px; 
        border-radius: 4px; margin-bottom: 4px; border-left: 3px solid #58a6ff; 
        background: #0d1117; color: #e6edf3; 
    }
    
    /* تنسيق زر التحميل ليكون مميزاً */
    .download-btn { margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- إدارة حالة البيانات ---
if "data" not in st.session_state:
    st.session_state.data = {"valid": [], "taken": [], "censored": [], "error": [], "unknown": []}
if "is_running" not in st.session_state: st.session_state.is_running = False

# --- الهيدر ---
st.title("🎯 Sniper User Roblox")
st.caption("Professional Bulk Username Hunter & Validator")

# --- التقسيم الرئيسي ---
left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.subheader("⚙️ Settings / الإعدادات")
    lang = st.radio("Language", ["English", "العربية"], horizontal=True, label_visibility="collapsed")
    is_ar = lang == "العربية"
    
    # 1. الحبل (Slider) يمتد بشكل حر من 100 إلى 100 ألف
    gen_limit = st.slider(
        "Generate Count" if not is_ar else "كمية التوليد",
        min_value=100, max_value=100000, value=1000, step=100
    )
    
    # 2. المسميات المطلوبة
    u_len = st.number_input(
        "Username Character Count" if not is_ar else "عدد احرف اليوزر", 
        min_value=3, max_value=20, value=4
    )
    u_prefix = st.text_input(
        "Username Starts With" if not is_ar else "يبداء اليوزر بـ", 
        placeholder="e.g. f5"
    )
    
    # 3. خيار الشرطة في أي مكان عدا الأطراف
    use_under = st.checkbox(
        "Add Underscore in Username" if not is_ar else "اضافة شرطة باليوزر"
    )

    st.markdown("---")
    
    # أزرار التشغيل
    if not st.session_state.is_running:
        if st.button("🚀 Start Sniper" if not is_ar else "🚀 ابدأ القنص"):
            st.session_state.is_running = True
            st.rerun()
    else:
        if st.button("🛑 Stop" if not is_ar else "🛑 إيقاف"):
            st.session_state.is_running = False
            st.rerun()

    if st.button("🗑️ Clear All" if not is_ar else "🗑️ مسح الكل"):
        st.session_state.data = {k: [] for k in st.session_state.data}
        st.rerun()

    # --- الزر المطلوب: حفظ اليوزرات المتاحة في ملف TXT ---
    if st.session_state.data["valid"]:
        st.markdown('<div class="download-btn">', unsafe_allow_html=True)
        valid_content = "\n".join(st.session_state.data["valid"])
        st.download_button(
            label="📥 Save Valid Users (.txt)" if not is_ar else "📥 حفظ المتاح في مستند txt",
            data=valid_content,
            file_name="valid_usernames.txt",
            mime="text/plain",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    # لوحة الإحصائيات
    total_found = sum(len(v) for v in st.session_state.data.values())
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TOTAL", f"{total_found}/{gen_limit}")
    m2.metric("VALID", len(st.session_state.data["valid"]))
    m3.metric("TAKEN", len(st.session_state.data["taken"]))
    m4.metric("CENSORED", len(st.session_state.data["censored"]))

    st.markdown("<br>", unsafe_allow_html=True)

    # التبويبات الخمسة
    tab_labels = ["✅ Valid", "❌ Taken", "🚫 Censored", "⚠️ Errors", "❓ Unknown"] if not is_ar \
                 else ["✅ متاح", "❌ مستخدم", "🚫 مبند", "⚠️ أخطاء", "❓ غير معروف"]
    tabs = st.tabs(tab_labels)
    
    cats = ["valid", "taken", "censored", "error", "unknown"]
    for i, cat in enumerate(cats):
        with tabs[i]:
            if not st.session_state.data[cat]:
                st.info("No results yet." if not is_ar else "لا توجد نتائج بعد.")
            else:
                for item in reversed(st.session_state.data[cat][-100:]):
                    st.markdown(f'<div class="user-entry">{item}</div>', unsafe_allow_html=True)

# --- محرك القنص ---
if st.session_state.is_running:
    chars = string.ascii_lowercase + string.digits
    while st.session_state.is_running and total_found < gen_limit:
        needed = max(0, u_len - len(u_prefix))
        body_pool = chars + ("_" if use_under else "")
        body = "".join(random.choices(body_pool, k=needed))
        user = u_prefix + body
        
        # التأكد من عدم وجود الشرطة في الأطراف
        if use_under and len(user) >= 3:
            u_list = list(user)
            if u_list[0] == "_": u_list[0] = random.choice(chars)
            if u_list[-1] == "_": u_list[-1] = random.choice(chars)
            user = "".join(u_list)

        try:
            r = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=3)
            if r.status_code == 200:
                code = r.json().get("code")
                if code == 0: st.session_state.data["valid"].append(user)
                elif code == 1: st.session_state.data["taken"].append(user)
                elif code == 2: st.session_state.data["censored"].append(user)
                else: st.session_state.data["unknown"].append(user)
            elif r.status_code == 429:
                time.sleep(2)
            else:
                st.session_state.data["error"].append(f"{user} ({r.status_code})")
        except:
            st.session_state.data["error"].append(f"Conn Error: {user}")
        
        total_found += 1
        st.rerun()

# --- الفوتر مع العبارة الوطنية ---
st.markdown(f"""
    <div class="footer">
        <span>Made in Saudi Arabia 🇸🇦</span>
        <span>Developed by: 7o.f | Discord: 7o.f</span>
    </div>
    """, unsafe_allow_html=True)
