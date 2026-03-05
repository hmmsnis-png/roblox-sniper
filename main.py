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
    h1 { color: #58a6ff !important; }
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
    </style>
    """, unsafe_allow_html=True)

# إدارة الحالة
if "data" not in st.session_state:
    st.session_state.data = {"valid": [], "taken": [], "censored": [], "error": [], "unknown": []}

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

    st.markdown("---")
    
    start_btn = st.button("🚀 Start Sniper" if not is_ar else "🚀 ابدأ القنص")
    
    if st.button("🗑️ Clear Results" if not is_ar else "🗑️ مسح النتائج"):
        st.session_state.data = {k: [] for k in st.session_state.data}
        st.rerun()

    # زر التحميل
    download_placeholder = st.empty()
    if st.session_state.data["valid"]:
        valid_text = "\n".join(st.session_state.data["valid"])
        download_placeholder.download_button(
            label="حفظ اليوزرات المتاحة بملف txt",
            data=valid_text,
            file_name="valid.txt",
            mime="text/plain",
            use_container_width=True
        )

with right_col:
    # حجز مكان للإحصائيات للتحديث بدون ريسيت
    stats_placeholder = st.empty()
    
    # حجز مكان للنتائج
    tabs_placeholder = st.empty()

# --- محرك التشغيل اللحظي (بدون ريسيت للصفحة كاملة) ---
if start_btn:
    chars = string.ascii_lowercase + string.digits
    checked_count = 0
    
    # هذه الحلقة ستعمل وتحدث العناصر المحجوزة فقط (Empty placeholders)
    while checked_count < gen_limit:
        # 1. توليد اليوزر (منطق الشرطة الإجبارية)
        needed = max(0, u_len - len(u_prefix))
        if use_under and needed > 1:
            body = list(random.choices(chars, k=needed))
            idx = random.randint(0, len(body) - 1)
            body[idx] = "_"
            user = u_prefix + "".join(body)
            # التأكد من الأطراف
            if user.startswith("_") or user.endswith("_"):
                user = user.replace("_", random.choice(chars), 1)
                mid_idx = random.randint(1, len(user)-2)
                user_list = list(user)
                user_list[mid_idx] = "_"
                user = "".join(user_list)
        else:
            user = u_prefix + "".join(random.choices(chars, k=needed))

        # 2. الفحص
        try:
            r = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=2)
            if r.status_code == 200:
                code = r.json().get("code")
                if code == 0: st.session_state.data["valid"].append(user)
                elif code == 1: st.session_state.data["taken"].append(user)
                elif code == 2: st.session_state.data["censored"].append(user)
                else: st.session_state.data["unknown"].append(user)
            elif r.status_code == 429:
                time.sleep(2)
        except:
            pass

        checked_count = sum(len(v) for v in st.session_state.data.values())

        # 3. التحديث اللحظي للواجهة (هنا السحر!)
        with stats_placeholder.container():
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("TOTAL", checked_count)
            m2.metric("VALID", len(st.session_state.data["valid"]))
            m3.metric("TAKEN", len(st.session_state.data["taken"]))
            m4.metric("CENSORED", len(st.session_state.data["censored"]))

        with tabs_placeholder.container():
            # عرض آخر النتائج في التبويبات بدون ريسيت للصفحة
            current_tab_labels = ["✅ Valid", "❌ Taken", "🚫 Censored", "⚠️ Errors", "❓ Unknown"] if not is_ar else ["✅ متاح", "❌ مستخدم", "🚫 مبند", "⚠️ أخطاء", "❓ غير معروف"]
            t1, t2, t3, t4, t5 = st.tabs(current_tab_labels)
            
            with t1: 
                for u in reversed(st.session_state.data["valid"][-10:]): st.markdown(f'<div class="user-entry">{u}</div>', unsafe_allow_html=True)
            with t2: 
                for u in reversed(st.session_state.data["taken"][-10:]): st.markdown(f'<div class="user-entry">{u}</div>', unsafe_allow_html=True)
            with t3: 
                for u in reversed(st.session_state.data["censored"][-10:]): st.markdown(f'<div class="user-entry">{u}</div>', unsafe_allow_html=True)
            # ... البقية متشابهة
        
        # وقت مستقطع بسيط جداً للسماح للمتصفح بالعرض
        time.sleep(0.01)

# الفوتر
st.markdown(f"""
    <div class="footer">
        <span>Made in Saudi Arabia 🇸🇦</span>
        <span>Developed by: 7o.f | Discord: 7o.f</span>
    </div>
    """, unsafe_allow_html=True)
