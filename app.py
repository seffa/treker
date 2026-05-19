import streamlit as st
import sqlite3
import os
from datetime import date, datetime, timedelta
import calendar
import base64
import streamlit.components.v1 as components

# ---------------- 1. КОНФИГУРАЦИЯ ----------------
st.set_page_config(page_title="Habit Tracker", layout="wide", initial_sidebar_state="expanded")

# Инициализация сессии (ДОЛЖНА БЫТЬ В САМОМ НАЧАЛЕ)
if "user" not in st.session_state:
    st.session_state.user = None

if "open_habit_dialog" not in st.session_state:
    st.session_state.open_habit_dialog = None

if "dialog_just_opened" not in st.session_state:
    st.session_state.dialog_just_opened = False


def local_css(style_path):
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("styles/style.css")


def get_db_connection():
    return sqlite3.connect('treker_bd.db', check_same_thread=False)


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS habits (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, name TEXT NOT NULL, duration INTEGER NOT NULL, icon_key TEXT)")

    # --- ПАТЧИ ДЛЯ СТАРЫХ ВЕРСИЙ БАЗЫ ДАННЫХ ---
    try:
        c.execute("ALTER TABLE habits ADD COLUMN icon_key TEXT")
    except:
        pass

    try:
        c.execute("ALTER TABLE habits ADD COLUMN duration INTEGER DEFAULT 30")
    except:
        pass
    # --------------------------------------------

    try:
        c.execute("ALTER TABLE habit_logs ADD COLUMN status TEXT DEFAULT 'done'")
    except:
        pass

    c.execute(
        "CREATE TABLE IF NOT EXISTS habit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER NOT NULL, log_date TEXT NOT NULL, status TEXT DEFAULT 'done', UNIQUE(habit_id, log_date))")
    c.execute(
        "CREATE TABLE IF NOT EXISTS user_settings (user_id INTEGER PRIMARY KEY, skip_double_click INTEGER DEFAULT 0, week_start TEXT DEFAULT 'Понедельник', font_size TEXT DEFAULT 'Средний')")
    conn.commit()
    conn.close()

init_db()


# Подгружаем настройки для применения в стилях
def load_settings(uid):
    conn = get_db_connection()
    res = conn.execute("SELECT week_start, font_size FROM user_settings WHERE user_id=?",
                       (uid,)).fetchone()
    conn.close()
    return res if res else ('Понедельник', 'Средний')


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


if st.session_state.user:
    u_id = st.session_state.user.get('id', 1)
    s_week, s_font = load_settings(u_id)
    f_size = "14px" if s_font == "Мелкий" else "25px" if s_font == "Крупный" else "17px"
    fdw = 0 if s_week == 'Понедельник' else 6
else:
    fdw, f_size = 0, "17px"

img1 = img_to_base64("styles/gj.png")
img2 = img_to_base64("styles/thumb.jpg")

# ---------------- 2. ФОНОВЫЕ ИЗОБРАЖЕНИЯ (СТАТИКА) ----------------
st.markdown(f"""
<style>
.bg-img {{
    position: fixed;
    top: 45px;
    z-index: 0;
    pointer-events: none;
}}

.bg-left {{
    left: 255px;
    width: 220px;
}}

.bg-right {{
    right: 95px;
    width: 180px;
}}
</style>

<img class="bg-img bg-left" src="data:image/png;base64,{img2}">
<img class="bg-img bg-right" src="data:image/jpeg;base64,{img1}">
""", unsafe_allow_html=True)

# ---------------- 3. СТИЛИ И ИНТЕГРАЦИЯ АДАПТИВА ----------------
st.markdown(f"""
<style>
.block-container {{ padding-top: 1rem !important; padding-bottom: 0rem !important; position: relative; z-index: 1;}}
[data-testid="stSidebarNav"] {{display: none;}}
section[data-testid="stSidebar"] {{ width: 150px !important; min-width: 150px !important; }}

/* Общий стиль для плиток и ссылок */
.nav-tile, [data-testid="stSidebar"] .stPageLink a {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 85px !important;
    height: 85px !important;
    margin: 15px auto !important;
    border-radius: 20px !important;
    color: white !important; 
    background-color: #8fa4bc !important;
    transition: all 0.3s ease !important;
    text-decoration: none !important;
    gap: 0 !important;
}}

[data-testid="stSidebar"] .stPageLink a div {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

[data-testid="stSidebar"] .stPageLink a p {{
    display: none !important;
    margin: 0 !important;
    padding: 0 !important;
    width: 0 !important;
    height: 0 !important;
}}

[data-testid="stSidebar"] .stPageLink a[aria-current="page"] {{
    background-color: #FF1493 !important;
}}

[data-testid="stSidebar"] .stPageLink a svg,
[data-testid="stSidebar"] .stPageLink a i,
[data-testid="stSidebar"] .stPageLink a span[translate="no"] {{
    font-size: 35px !important;
    width: 35px !important;
    height: 35px !important;
    line-height: 35px !important;
    margin: 0 !important; 
    padding: 0 !important;
    display: block !important;
    fill: white !important; 
    color: white !important; 
}}

[data-testid="stSidebar"] .stPageLink a:hover {{
    background-color: #70869d !important;
    transform: scale(1.05);
}}

.stButton > button {{
    background-color: #6B7B94 !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: 600 !important;
    transition: 0.2s ease;
}}

.stButton > button:hover {{
    background-color: #6B7B94 !important;
    transform: scale(1.02);
}}

.page-header {{ text-align: center; margin: 30px 0; font-size: 32px; font-weight: 700; color: #334455; }}

.habits-grid {{
    display: block;
    padding: 20px;
}}

.habit-card {{
    background: #ffffff;
    border-radius: 28px;
    width: 210px;
    height: 240px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 1.5px solid #E0E6ED;
    position: relative;
    margin: 0 auto 15px auto;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
    overflow: hidden;
}}

.habit-card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 20px 40px rgba(91, 141, 190, 0.2);
    border-color: #5B8DBE;
}}

.habit-avatar {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4A90E2 0%, #5B8DBE 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 15px;
    box-shadow: 0 8px 20px rgba(74, 144, 226, 0.35);
}}

.habit-avatar i, .habit-avatar span {{
    font-size: 32px !important;
    color: #ffffff !important; 
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}}

.habit-name {{
    color: #111111; 
    font-size: {f_size};
    font-weight: 800; 
    text-align: center;
    padding: 0 15px;
    line-height: 1.1;
}}

.habit-meta {{
    color: #556677; 
    font-size: {f_size};
    margin-top: 8px;
    font-weight: 600;
}}

.progress-bar {{
    position: absolute;
    bottom: 18px;
    left: 25px;
    right: 25px;
    height: 10px; 
    background: #EDF1F7;
    border-radius: 20px;
}}

.progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, #4A90E2, #007AFF);
    border-radius: 20px;
}}

/* Выбор иконок */
div[role="radiogroup"] {{
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    justify-content: center;
    margin-bottom: 10px;
}}

div[role="radiogroup"] label {{
    width: 80px !important;  
    height: 60px !important;
    background: #EAF4FF;
    border-radius: 16px;
    cursor: pointer;
    transition: 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none !important;
}}

div[role="radiogroup"] [data-baseweb="radio"] > div:first-child,
div[role="radiogroup"] [data-testid="stWidgetSelectionVisualizer"] {{
    display: none !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
}}

div[role="radiogroup"] label p {{
    font-family: 'Material Icons' !important;
    font-size: 32px !important;
    color: #334455 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
    width: 100% !important;
}}

div[role="radiogroup"] label:hover {{
    background: #D6E9FF !important;
}}

div[role="radiogroup"] input:checked + div {{
    background: #4DA6FF !important;
    border-radius: 16px !important;
}}

div[role="radiogroup"] input:checked + div p {{
    color: white !important; 
}}

/* Ползунок слайдера */
div[data-testid="stSlider"] [role="slider"] {{
    background-color: #5B8DBE !important;
    border-color: #5B8DBE !important;
    box-shadow: none !important;
}}

div[data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {{
    background-color: #5B8DBE !important;
}}

div[data-testid="stSlider"] * {{
    color: #5B8DBE !important;
    --primary-color: #5B8DBE !important;
}}

div[data-testid="stSlider"] [data-baseweb="slider"] > div {{
    background-image: none !important;
    background-color: transparent !important;
}}

div[data-testid="stSlider"] [data-baseweb="slider"] div[style*="left: 0%"] {{
    background-color: #5B8DBE !important;
}}

/* Кнопки под карточками */
div.stButton > button[id*="btn_info_"],
div.stButton > button[id*="st-key-btn_check_"],
div.stButton > button[id*="st-key-btn_done_"] {{
    background-color: #F0F4F8 !important;
    color: #111111 !important;
    border: 1px solid #D0DCE8 !important;
    font-weight: 700 !important;
    width: 50px !important;
    height: 50px !important;
    min-width: 50px !important;
    max-width: 50px !important;
    padding: 0 !important;
    aspect-ratio: 1 / 1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

div[data-testid="column"]:has(button[id*="btn_info_"]) {{
    display: flex !important;
    justify-content: flex-start !important;
}}

div[data-testid="column"]:has(button[id*="btn_check_"]), 
div[data-testid="column"]:has(button[id*="btn_done_"]) {{
    display: flex !important;
    justify-content: flex-end !important;
}}

[data-testid="stVerticalBlock"]:has(button[id*="add_habit_btn"]) {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    width: 100% !important;
}}

div.stButton:has(button[id*="add_habit_btn"]) {{
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}}

button[id*="add_habit_btn"] {{
    width: 300px !important;
    height: 50px !important;
    margin: 0 auto !important;
    background-color: #6B7B94 !important;
    color: white !important;
    display: block !important;
}}

button[id*="btn_done_"]:disabled {{
    background: #28C76F !important;
    color: #ffffff !important;
    border: none !important;
    opacity: 1 !important; 
}}

/* --- УМНАЯ МАСКИРОВКА ХЕДЕРА --- */
footer, #MainMenu {{ visibility: hidden; display: none; }}
header[data-testid="stHeader"] {{
    visibility: hidden !important; 
    background: transparent !important;
}}

header[data-testid="stHeader"] button {{
    visibility: visible !important; 
    color: #8fa4bc !important; 
}}

/* -----------------------------------------------------------------
   ПОЛНЫЙ МОБИЛЬНЫЙ АДАПТИВ (ВКЛЮЧАЯ ХИРУРГИЧЕСКИЙ ФИКС КАЛЕНДАРЯ)
   ----------------------------------------------------------------- */
@media (max-width: 768px) {{
    .bg-img, .img3 {{
        display: none !important;
    }}

    section[data-testid="stSidebar"] {{
        width: 125px !important;
        min-width: 125px !important;
        max-width: 125px !important;
    }}

    .nav-tile, [data-testid="stSidebar"] .stPageLink a {{
        width: 75px !important;
        height: 75px !important;
        margin: 12px auto !important;
        border-radius: 18px !important;
    }}

    [data-testid="stSidebar"] .stPageLink a svg,
    [data-testid="stSidebar"] .stPageLink a i,
    [data-testid="stSidebar"] .stPageLink a span[translate="no"] {{
        font-size: 30px !important;
        width: 30px !important;
        height: 30px !important;
        line-height: 30px !important;
    }}

    button[id*="add_habit_btn"], .stButton > button {{
        width: 100% !important;
        max-width: 100% !important;
    }}

    .page-header {{
        font-size: 24px !important;
        margin-top: 20px !important;
        margin-bottom: 30px !important;
    }}

    .habit-card {{
        width: 100% !important;
        max-width: 260px;
        margin: 0 auto 15px auto !important;
    }}

    /* --- ЖЕСТКИЙ ФИКС ДЛЯ КАЛЕНДАРЯ В МОДАЛКЕ НА МОБИЛЬНЫХ --- */
    div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 3px !important;
        width: 100% !important;
    }}

    /* Фиксируем строки, где ровно 7 колонок (дни недели и числа) */
    div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-last-child(7):first-child) > div[data-testid="column"] {{
        width: calc(100% / 7) !important;
        min-width: calc(100% / 7) !important;
        max-width: calc(100% / 7) !important;
        flex: 1 1 calc(100% / 7) !important;
        padding: 0 !important;
        margin: 0 !important;
    }}

    /* Фиксируем строку переключения месяцев (3 колонки: стрелка, месяц, стрелка) */
    div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-last-child(3):first-child) > div[data-testid="column"] {{
        width: auto !important;
        flex: 1 !important;
    }}

    /* Сжимаем ячейки с числами, чтобы помещались в один экран */
    div[data-testid="stDialog"] div[style*="margin:4px"] {{
        margin: 2px 1px !important;
        padding: 5px 1px !important;
        font-size: 11px !important;
        border-radius: 6px !important;
    }}

    /* Корректируем индикатор галочки выполненного дня */
    div[data-testid="stDialog"] div[style*="position:absolute"] {{
        font-size: 8px !important;
        bottom: 1px !important;
        right: 2px !important;
    }}

    /* Сужаем отступы блока серий/пламени */
    div[style*="display:flex; justify-content:center; gap:60px;"] {{
        gap: 25px !important;
    }}
}}
</style>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
""", unsafe_allow_html=True)

# ---------------- 4. НАДЕЖНЫЙ САЙДБАР ----------------
with st.sidebar:
    st.markdown('<div class="nav-tile"><i class="material-icons" style="font-size:40px;">menu</i></div>',
                unsafe_allow_html=True)
    st.page_link("app.py", label="Home", icon=":material/home:")
    st.page_link("pages/profile2.py", label="Profile", icon=":material/person:")
    st.page_link("pages/settings2.py", label="Settings", icon=":material/settings:")
    st.page_link("pages/contacts2.py", label="Chat", icon=":material/chat:")

# ---------------- 5. ПРОВЕРКА АВТОРИЗАЦИИ ----------------
if not st.session_state.user:
    st.markdown('<div class="page-header">ГЛАВНАЯ</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("Чтобы увидеть свои привычки, нужно войти в аккаунт.")
        if st.button("Перейти к входу", use_container_width=True, type="primary"):
            st.switch_page("pages/profile2.py")
    st.stop()

USER_ID = st.session_state.user.get('id', 1)

# ---------------- 6. ФУНКЦИИ И ДИАЛОГИ ----------------
ICONS = {
    "run": "directions_run", "water": "water_drop", "sleep": "bedtime",
    "study": "school", "gym": "fitness_center", "food": "restaurant",
    "walk": "directions_walk", "meditate": "self_improvement",
    "target": "track_changes", "analyse": "query_stats",
    "time": "schedule", "health": "medical_services"
}


def calculate_streaks(history):
    if not history:
        return 0, 0
    dates = sorted(set(history))
    dates = [datetime.fromisoformat(d).date() for d in dates]

    max_streak = 1
    cur = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            cur += 1
            max_streak = max(max_streak, cur)
        else:
            cur = 1

    today = date.today()
    streak = 0
    d = today
    while d.isoformat() in history:
        streak += 1
        d -= timedelta(days=1)
    return streak, max_streak


@st.dialog("Новая цель")
def add_habit_dialog():
    name = st.text_input("Название:")
    duration = st.slider("Цель (дней):", 1, 100, 30)

    selected_icon_name = st.radio(
        "Выберите иконку",
        list(ICONS.values()),
        horizontal=True,
        label_visibility="collapsed"
    )

    icon_key = [k for k, v in ICONS.items() if v == selected_icon_name][0]

    if st.button("Создать", use_container_width=True, type="primary"):
        user_data = st.session_state.get('user')
        current_id = user_data.get('id') if user_data else None

        if current_id is None:
            st.error("Ошибка: ID пользователя не найден. Попробуйте перезайти.")
            return

        if name.strip():
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute(
                    "INSERT INTO habits (user_id, name, duration, icon_key) VALUES (?, ?, ?, ?)",
                    (current_id, name.strip(), duration, icon_key)
                )
                conn.commit()
                conn.close()
                st.rerun()
            except sqlite3.IntegrityError as e:
                st.error(f"Ошибка базы данных: {e}")


@st.dialog(" ")
def habit_dialog(h_id, h_name, history):
    st.session_state.open_habit_dialog = (h_id, h_name, history)
    st.session_state.dialog_just_opened = True
    today = date.today()
    key_month, key_year = f"month_{h_id}", f"year_{h_id}"
    st.session_state.setdefault(key_month, today.month)
    st.session_state.setdefault(key_year, today.year)
    month, year = st.session_state[key_month], st.session_state[key_year]

    st.markdown(
        "<h3 style='text-align:center; margin-bottom:15px; font-family: Tahoma; font-weight:800;'>КАЛЕНДАРЬ</h3>",
        unsafe_allow_html=True
    )

    # УБРАНА ОШИБКА РАЗМЕТКИ: Колонки навигации теперь чистые и симметричные без вложенности
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("←", key=f"prev_{h_id}", use_container_width=True):
            st.session_state[key_month] = 12 if month == 1 else month - 1
            st.session_state[key_year] = year - 1 if month == 1 else year
            st.rerun()

    with col2:
        st.markdown(
            f"<div style='text-align:center; font-weight:600; line-height:2.4;'>{calendar.month_name[month]} {year}</div>",
            unsafe_allow_html=True
        )

    with col3:
        if st.button("→", key=f"next_{h_id}", use_container_width=True):
            st.session_state[key_month] = 1 if month == 12 else month + 1
            st.session_state[key_year] = year + 1 if month == 12 else year
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    cal = calendar.Calendar(firstweekday=fdw)
    month_days = cal.monthdayscalendar(year, month)

    if fdw == 0:
        week_days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
    else:
        week_days = ["ВС", "ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ"]

    cols = st.columns(7)
    for i_d, d in enumerate(week_days):
        cols[i_d].markdown(
            f"<div style='text-align:center; font-family: Tahoma; font-weight:600; margin-bottom: 10px; color:#667'>{d}</div>",
            unsafe_allow_html=True)

    for week in month_days:
        cols = st.columns(7)
        for i_d, day in enumerate(week):
            if day == 0:
                cols[i_d].markdown(" ")
            else:
                d_obj = date(year, month, day)
                d_str = d_obj.isoformat()
                done = d_str in history
                is_today = d_obj == today
                bg = "#5B8DBE" if done else "#F1F4F8"
                color = "white" if done else "#334455"
                border = "2px solid #5B8DBE" if is_today else "1px solid transparent"
                cols[i_d].markdown(f"""
                    <div style="margin:4px; padding:10px; border-radius:10px; background:{bg}; color:{color};
                                text-align:center; font-weight:600; border:{border}; position:relative;">
                        {day}
                        {"<div style='position:absolute; bottom:4px; right:6px; font-size:12px;'>✓</div>" if done else ""}
                    </div>
                """, unsafe_allow_html=True)

    streak, max_streak = calculate_streaks(history)
    today_done = today.isoformat() in history

    # Флаг приведен к компактной однострочной записи для стабильного рендеринга
    flame = lambda active: f'<span style="font-family:\'Material Icons\'; font-size:24px; color:{"#007AFF" if active else "#BCBCC2"}; vertical-align:middle;">local_fire_department</span>'

    st.markdown(f"""
    <div style="display:flex; justify-content:center; gap:60px; margin-top:20px; margin-bottom:0px;">
        <div style="display:flex; flex-direction:column; align-items:center;">
            <div style="display:flex; align-items:center; gap:6px;">
                {flame(today_done)} 
                <span style="font-size:22px; font-weight:800;">{streak}</span>
            </div>
            <div style="margin-top:1px; font-size:13px; color:#667; line-height:1;">текущая серия</div>
        </div>
        <div style="display:flex; flex-direction:column; align-items:center;">
            <div style="display:flex; align-items:center; gap:6px;">
                {flame(True)} 
                <span style="font-size:22px; font-weight:800;">{max_streak}</span>
            </div>
            <div style="margin-top:1px; font-size:13px; color:#667; line-height:1;">максимальная серия</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.write("---")
    if st.button("Удалить привычку", type="secondary", use_container_width=True):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM habits WHERE id = ?", (h_id,))
        c.execute("DELETE FROM habit_logs WHERE habit_id = ?", (h_id,))
        conn.commit()
        conn.close()
        st.session_state.open_habit_dialog = None
        st.rerun()


if st.session_state.open_habit_dialog and st.session_state.dialog_just_opened:
    h_id, h_name, hist = st.session_state.open_habit_dialog
    habit_dialog(h_id, h_name, hist)
    st.session_state.dialog_just_opened = False

# ---------------- 7. ГЛАВНЫЙ ЭКРАН ----------------
st.markdown('<div class="page-header">ГЛАВНАЯ</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Добавить привычку", type="primary", key="add_habit_btn", use_container_width=True):
        add_habit_dialog()

st.markdown('<div style="margin-bottom: 40px;"></div>', unsafe_allow_html=True)

# Загрузка данных
conn = get_db_connection()
c = conn.cursor()
c.execute("""
    SELECT h.id, h.name, h.duration, h.icon_key,
    (SELECT COUNT(*) FROM habit_logs WHERE habit_id = h.id AND status = 'done') as progress,
    (SELECT status FROM habit_logs WHERE habit_id = h.id AND log_date = ?) as t_status
    FROM habits h WHERE h.user_id = ?
""", (date.today().isoformat(), USER_ID))
habits = c.fetchall()
conn.close()

if habits:
    cols = st.columns(4)

    for idx, (h_id, h_name, h_dur, h_icon, h_prog, t_status) in enumerate(habits):
        progress_pct = min(100, int((h_prog / h_dur) * 100))
        icon_name = ICONS.get(h_icon, "star")

        with cols[idx % 4]:
            st.markdown(f"""
                <div class="habit-card">
                    <div class="habit-avatar">
                        <i class="material-icons" style="font-size:42px; color: white;">{icon_name}</i>
                    </div>
                    <div class="habit-name">{h_name}</div>
                    <div class="habit-meta">{h_prog}/{h_dur} дн.</div>
                    <div class="progress-bar"><div class="progress-fill" style="width:{progress_pct}%"></div></div>
                </div>
            """, unsafe_allow_html=True)

            b_col_space1, b_col1, b_col2, b_col_space2 = st.columns(4)

            with b_col1:
                if st.button("", icon=":material/calendar_month:", key=f"btn_info_{h_id}"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("SELECT log_date FROM habit_logs WHERE habit_id = ? AND status='done'", (h_id,))
                    hist = [r[0] for r in c.fetchall()]
                    conn.close()

                    st.session_state.open_habit_dialog = (h_id, h_name, hist)
                    st.session_state.dialog_just_opened = True
                    st.rerun()

            with b_col2:
                if not t_status:
                    if st.button("", icon=":material/check_circle:", key=f"btn_check_{h_id}"):
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute(
                            "INSERT OR REPLACE INTO habit_logs (habit_id, log_date, status) VALUES (?, ?, 'done')",
                            (h_id, date.today().isoformat()))
                        conn.commit()
                        conn.close()
                        st.rerun()
                else:
                    st.button("", icon=":material/task_alt:", key=f"btn_done_{h_id}", disabled=True)

else:
    st.write("---")
    st.info("Привычек пока нет. Самое время начать что-то новое!")
