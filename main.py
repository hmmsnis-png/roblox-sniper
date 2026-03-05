import streamlit as st
import requests
import time
import random
import string

# --- إعدادات الصفحة ---
st.set_page_config(page_title="RBLX Checker | 7o.f", page_icon="🟦", layout="wide")

# --- تنسيق CSS المخصص لمحاكاة الصورة ---
st.markdown("""
    <style>
    /* الخلفية العامة */
    .stApp { background-color: #0d1117; color: #adbac7; }
    
    /* الحاويات الجانبية */
    [data-testid="stVerticalBlock"] > div:has(div.element-container) {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px;
    }

    /* أزرار مخصصة */
    .stButton>button {
        width: 100%; border-radius: 8px; background-color: #1f6feb; color: white;
        border: none; transition: 0.3s; font-weight: 600;
    }
    .stButton>button:hover { background-color: #388bfd; transform: translateY(-2px); }
    
    /* العناوين والإحصائيات */
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Inter', sans-serif; }
    .metric-card { text-align: center; border-right: 1px solid #30363d; }
    
    /* الفوتر */
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0d1117; 
              text-align: center; color: #58a6ff; padding: 10px; border-top: 1px solid #30363d; font-size: 14px; }
    
    /* تبويبات النتائج */
    .stTabs [data-baseweb="tab-list"] { background-color: #0d1117; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: #adbac7 !important; }
    .stTabs [aria-selected="true"] { color: #58a6ff !important; border-bottom-color: #58a6ff !important; }

    /* مظهر اليوزرات في القائمة */
    .user-entry { font-family: 'Source Code Pro', monospace; padding: 5px 10px; border-radius: 4px; margin-bottom: 4px; border-left: 3px solid #58a6ff; background: #0d1117; }
    </style>
    """, unsafe_allow_html=True)

# --- إدارة الحالة ---
if "data" not in st.session_state:
    st.session_state.data = {"valid": [], "taken": [], "censored": [], "error": [], "unknown": []}
if "running" not in st.session_state: st.session_state.running = False

# --- الهيدر العلوي ---
col_logo, col_nav = st.columns([2, 1])
with col_logo:
    st.title("🟦 RBLX Checker")
    st.caption("High-performance bulk username availability validation.")

# --- الواجهة الرئيسية (تقسيم مشابه للصورة) ---
left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.subheader("📥 Input Settings")
    
    # خيار اللغة
    lang = st.radio("Language / اللغة", ["English", "العربية"], horizontal=True)
    is_ar = lang == "العربية"
    
    # سلايدر العدد (الحبل)
    gen_limit = st.select_slider(
        "Generate Count" if not is_ar else "كمية التوليد",
        options=[100, 500, 1000, 5000, 10000, 50000, 100000],
        value=1000
    )
    
    # خيارات اليوزر
    u_len = st.number_input("Length" if not is_ar else "الطول", 3, 20, 4)
    u_prefix = st.text_input("Starts with" if not is_ar else "يبدأ بـ", placeholder="e.g. f5")
    use_under = st.checkbox("Include '_' (Middle only)" if not is_ar else "إضافة شرطة (في الوسط فقط)")

    st.markdown("---")
    
    # أزرار التحكم
    if not st.session_state.running:
        if st.button(f"✨ Start Checking" if not is_ar else "✨ ابدأ الفحص"):
            st.session_state.running = True
            st.rerun()
    else:
        if st.button("🛑 Stop" if not is_ar else "🛑 إيقاف"):
            st.session_state.running = False
            st.rerun()

    if st.button("🗑️ Clear Results" if not is_ar else "🗑️ مسح النتائج"):
        st.session_state.data = {k: [] for k in st.session_state.data}
        st.rerun()

with right_col:
    # لوحة الإحصائيات العلوي (Progress & Counts)
    total_found = sum(len(v) for v in st.session_state.data.values())
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("PROGRESS", f"{total_found}/{gen_limit}")
    m2.metric("AVAILABLE", len(st.session_state.data["valid"]))
    m3.metric("TAKEN", len(st.session_state.data["taken"]))
    m4.metric("CENSORED", len(st.session_state.data["censored"]))

    st.markdown("<br>", unsafe_allow_html=True)

    # التبويبات (الخيارات الخمسة)
    tabs = st.tabs(["✅ Valid", "❌ Taken", "🚫 Censored", "⚠️ Errors", "❓ Unknown"] if not is_ar 
                   else ["✅ متاح", "❌ مستخدم", "🚫 مبند", "⚠️ أخطاء", "❓ غير معروف"])
    
    categories = ["valid", "taken", "censored", "error", "unknown"]
    
    for i, cat in enumerate(categories):
        with tabs[i]:
            if not st.session_state.data[cat]:
                st.info("Awaiting validation..." if not is_ar else "بانتظار الفحص...")
            else:
                for item in reversed(st.session_state.data[cat][-50:]): # عرض آخر 50
                    st.markdown(f'<div class="user-entry">{item}</div>', unsafe_allow_html=True)

# --- محرك التشغيل ---
if st.session_state.running:
    chars = string.ascii_lowercase + string.digits
    
    # تنفيذ الفحص
    for _ in range(gen_limit - total_found):
        if not st.session_state.running: break
        
        # إنشاء اليوزر مع شروطك
        needed = max(0, u_len - len(u_prefix))
        body_pool = chars + ("_" if use_under else "")
        body = "".join(random.choices(body_pool, k=needed))
        user = u_prefix + body
        
        # تصحيح مكان الشرطة السفلية (ممنوع في البداية أو النهاية)
        if len(user) > 2 and "_" in user:
            u_list = list(user)
            if u_list[0] == "_": u_list[0] = random.choice(chars)
            if u_list[-1] == "_": u_list[-1] = random.choice(chars)
            user = "".join(u_list)

        try:
            res = requests.get(f"https://auth.roblox.com/v1/usernames/validate?Username={user}&Birthday=2000-01-01", timeout=3)
            if res.status_code == 200:
                code = res.json().get("code")
                if code == 0: st.session_state.data["valid"].append(user)
                elif code == 1: st.session_state.data["taken"].append(user)
                elif code == 2: st.session_state.data["censored"].append(user)
                else: st.session_state.data["unknown"].append(user)
            elif res.status_code == 429:
                time.sleep(5) # حماية من الحظر
            else:
                st.session_state.data["error"].append(f"{user} ({res.status_code})")
        except:
            st.session_state.data["error"].append(f"Conn Error: {user}")

        st.rerun()

# الفوتر (حقوقك)
st.markdown(f'<div class="footer">Developed by: 7o.f | Discord: 7o.f</div>', unsafe_allow_html=True)
