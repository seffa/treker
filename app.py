import streamlit as st
import sqlite3
import os
from datetime import date, datetime, timedelta
import calendar

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


# ---------------- 2. БАЗА ДАННЫХ ----------------
def get_db_connection():
    return sqlite3.connect('treker_bd.db', check_same_thread=False)


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            duration INTEGER NOT NULL,
            description TEXT,
            icon_key TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            UNIQUE(habit_id, log_date)
        )
    """)
    conn.commit()
    conn.close()


init_db()

# ---------------- 3. СТИЛИ ----------------
st.markdown("""
<style>
.block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }

/* --- НАВИГАЦИЯ (САЙДБАР) --- */
[data-testid="stHeader"] { background: rgba(0,0,0,0); } /* Прозрачный хедер */
[data-testid="stSidebarNav"] {display: none;}
section[data-testid="stSidebar"] { width: 150px !important; min-width: 150px !important; }

/* Общий стиль для плиток и ссылок */
.nav-tile, [data-testid="stSidebar"] .stPageLink a {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 85px !important;
    height: 85px !important;
    margin: 15px auto !important;
    border-radius: 20px !important;
    color: white !important; /* Цвет текста/иконки */
    background-color: #8fa4bc !important;
    transition: all 0.3s ease !important;
    text-decoration: none !important;
    /* Убираем стандартный зазор между иконкой и скрытым текстом */
    gap: 0 !important; 
}

/* ИСПРАВЛЕНИЕ ЦЕНТРИРОВАНИЯ: Сбрасываем внутренние контейнеры Streamlit */
[data-testid="stSidebar"] .stPageLink a div {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Полностью убираем влияние текста */
[data-testid="stSidebar"] .stPageLink a p {
    display: none !important;
    margin: 0 !important;
    padding: 0 !important;
    width: 0 !important;
    height: 0 !important;
}

/* Ссылка в активном состоянии */
[data-testid="stSidebar"] .stPageLink a[aria-current="page"] { 
    background-color: #FF1493 !important; 
}

/* СТИЛИЗАЦИЯ ИКОНОК: Убираем лишние отступы */
[data-testid="stSidebar"] .stPageLink a svg,
[data-testid="stSidebar"] .stPageLink a i,
[data-testid="stSidebar"] .stPageLink a span[translate="no"] {
    font-size: 35px !important; 
    width: 35px !important;
    height: 35px !important;
    line-height: 35px !important;
    margin: 0 !important; /* Обнуляем margin, который Streamlit добавляет справа */
    padding: 0 !important;
    display: block !important;
    fill: white !important; /* Для SVG */
    color: white !important; /* Для шрифтовых иконок */
}

/* Ховер эффект */
[data-testid="stSidebar"] .stPageLink a:hover {
    background-color: #70869d !important;
    transform: scale(1.05);
}
header, footer, #MainMenu { visibility: hidden; display: none; }

.stButton > button {
    background-color: #6B7B94 !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: 600 !important;
    transition: 0.2s ease;
}
.stButton > button:hover {
    background-color: #6B7B94 !important;
    transform: scale(1.02);
}

.page-header { text-align: center; margin: 30px 0; font-size: 32px; font-weight: 700; color: #334455; }

.habits-grid { 
    display: block; 
    padding: 20px; 
}

.habit-card {
    background: #ffffff;
    border-radius: 28px;
    width: 210px;
    height: 240px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    /* Усилили рамку */
    border: 1.5px solid #E0E6ED; 
    position: relative;
    margin: 0 auto 15px auto; 

    /* Более выраженная тень для объема */
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08); 
    transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
    overflow: hidden;
}

.habit-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 40px rgba(91, 141, 190, 0.2);
    border-color: #5B8DBE;
}

.habit-avatar {
    width: 80px; 
    height: 80px;
    border-radius: 50%;
    /* ГЛУБОКИЙ КОНТРАСТНЫЙ ГРАДИЕНТ: от синего к насыщенному голубому */
    background: linear-gradient(135deg, #4A90E2 0%, #5B8DBE 100%);
    display: flex; 
    align-items: center; 
    justify-content: center;
    margin-bottom: 15px;
    /* Тень под иконкой, чтобы она "вдавливалась" или "выступала" */
    box-shadow: 0 8px 20px rgba(74, 144, 226, 0.35);
}

/* Сама иконка теперь максимально видна */
.habit-avatar i, .habit-avatar span {
    font-size: 36px !important;
    color: #ffffff !important; /* Яркий белый на темном фоне */
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.habit-name { 
    color: #111111; /* Чистый черный или очень темный для четкости */
    font-size: 17px; 
    font-weight: 800; /* Максимально жирный */
    text-align: center; 
    padding: 0 15px;
    line-height: 1.1;
}

.habit-meta { 
    color: #556677; /* Затемнили текст подписи */
    font-size: 13px; 
    margin-top: 8px; 
    font-weight: 600;
}

/* Прогресс-бар: сделали ярче и заметнее */
.progress-bar {
    position: absolute; 
    bottom: 18px; 
    left: 25px; 
    right: 25px;
    height: 10px; /* Сделали чуть толще */
    background: #EDF1F7; 
    border-radius: 20px; 
}

.progress-fill { 
    height: 100%; 
    /* Насыщенный синий для заполнения */
    background: linear-gradient(90deg, #4A90E2, #007AFF); 
    border-radius: 20px;
}

/* ---------------- КНОПКИ (АКЦЕНТЫ) ---------------- */
div.stButton > button[id^="st-key-btn_info_"],
div.stButton > button[id^="st-key-btn_check_"],
div.stButton > button[id^="st-key-btn_done_"] {
    background-color: #F0F4F8 !important;
    color: #111111 !important; /* Текст кнопок стал черным */
    border: 1px solid #D0DCE8 !important;
    font-weight: 700 !important;
}

div.stButton > button[id^="st-key-btn_"]:hover {
    background-color: #5B8DBE !important;
    color: #ffffff !important;
    border-color: #5B8DBE !important;
}

/* Галочка (выполнено) — теперь сочный зеленый */
div.stButton > button[id^="st-key-btn_done_"]:disabled {
    background: #28C76F !important; /* Яркий зеленый */
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(40, 199, 111, 0.3) !important;
}

/* ---------------- ВЫБОР ИКОНКИ ПРИ СОЗДАНИИ (MATERIAL ICONS) ---------------- */
div[role="radiogroup"] {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    justify-content: center;
    margin-bottom: 10px;
}

div[role="radiogroup"] label {
    width: 80px !important;  /* Сделаем чуть шире, чтобы текст не вылезал, пока грузится шрифт */
    height: 60px !important;
    background: #EAF4FF;
    border-radius: 16px;
    cursor: pointer;
    transition: 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none !important;
}

/* Скрываем стандартный кружок радио-кнопки */
div[role="radiogroup"] [data-testid="stWidgetSelectionVisualizer"] {
    display: none !important;
    opacity: 0 !important;
}

/* ПРОБИВАЕМ ШРИФТ: Нацеливаемся прямо на параграф с текстом внутри лейбла */
div[role="radiogroup"] label p {
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
}

/* Цвет иконки при наведении */
div[role="radiogroup"] label:hover {
    background: #D6E9FF !important;
}

/* Цвет иконки и фона при выборе */
div[role="radiogroup"] input:checked + div {
    background: #4DA6FF !important;
    border-radius: 16px !important;
}

div[role="radiogroup"] input:checked + div p {
    color: white !important; /* Иконка становится белой на синем фоне */
}

/* 4. Принудительно красим сам ползунок и активную дорожку в синий */
div[data-testid="stSlider"] [role="slider"] {
    background-color: #5B8DBE !important;
    border-color: #5B8DBE !important;
    box-shadow: none !important;
}

div[data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {
    background-color: #5B8DBE !important;
}

/* Нацеливаемся на все внутренние элементы текста и ползунка */
div[data-testid="stSlider"] * {
    color: #5B8DBE !important;
    --primary-color: #5B8DBE !important;
}

div[data-testid="stSlider"] [data-baseweb="slider"] > div {
    background-image: none !important;
    background-color: transparent !important;
}

/* Принудительно красим активную часть дорожки (до ползунка) в синий */
div[data-testid="stSlider"] [data-baseweb="slider"] div[style*="left: 0%"] {
    background-color: #5B8DBE !important;
}

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
# ИСПРАВЛЕНИЕ: Заменил эмодзи на названия Material Icons
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
        if name.strip():
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO habits (user_id, name, duration, description, icon_key) VALUES (?, ?, ?, ?, ?)",
                      (USER_ID, name.strip(), duration, "", icon_key))
            conn.commit()
            conn.close()
            st.rerun()

@st.dialog(" ")
def habit_dialog(habit, i, history):
    st.session_state.open_habit_dialog = (h_id, h_name, hist)
    st.session_state.dialog_just_opened = True
    today = date.today()
    key_month, key_year = f"month_{i}", f"year_{i}"
    st.session_state.setdefault(key_month, today.month)
    st.session_state.setdefault(key_year, today.year)
    month, year = st.session_state[key_month], st.session_state[key_year]

    st.markdown(f"<h3 style='text-align:center; margin-bottom:10px;'>КАЛЕНДАРЬ</h3>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("←", key=f"prev_{i}"):
            st.session_state[key_month] = 12 if month == 1 else month - 1
            st.session_state[key_year] = year - 1 if month == 1 else year
            st.rerun()
    with col2:
        st.markdown(f"<div style='text-align:center; font-weight:600'>{calendar.month_name[month]} {year}</div>",
                    unsafe_allow_html=True)
    with col3:
        if st.button("→", key=f"next_{i}"):
            st.session_state[key_month] = 1 if month == 12 else month + 1
            st.session_state[key_year] = year + 1 if month == 12 else year
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    #history = habit.get("history", [])
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    week_days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
    cols = st.columns(7)
    for i_d, d in enumerate(week_days):
        cols[i_d].markdown(f"<div style='text-align:center; font-weight:600; color:#667'>{d}</div>",
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
    flame = lambda \
        active: f'<svg width="24" height="24" viewBox="0 0 24 24"><path fill="{"#2735F5" if active else "#BCBCC2"}" d="M13 2C13 2 8 8 8 12a4 4 0 0 0 8 0c0-3-3-7-3-10z"/><path fill="{"#FFA726" if active else "#BCBCC2"}" d="M12 14a2 2 0 0 0 2-2c0-1.5-1.5-3-2-4-0.5 1-2 2.5-2 4a2 2 0 0 0 2 2z"/></svg>'

    c1, c2 = st.columns(2)
    c1.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;">{flame(today_done)} <b>{streak}</b> Текущ.</div>',
        unsafe_allow_html=True)
    c2.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;">{flame(True)} <b>{max_streak}</b> Макс.</div>',
        unsafe_allow_html=True)
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

col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    if st.button("Добавить привычку", use_container_width=True, type="primary"):
        add_habit_dialog()

st.markdown('<div style="margin-bottom: 70px;"></div>', unsafe_allow_html=True)

# Загрузка данных
conn = get_db_connection()
c = conn.cursor()
c.execute("""
    SELECT h.id, h.name, h.duration, h.icon_key,
    (SELECT COUNT(*) FROM habit_logs WHERE habit_id = h.id) as progress,
    (SELECT 1 FROM habit_logs WHERE habit_id = h.id AND log_date = ?) as done_today
    FROM habits h WHERE h.user_id = ?
""", (date.today().isoformat(), USER_ID))
habits = c.fetchall()
conn.close()

if habits:
    cols = st.columns(4)  # Основная сетка карточек

    for idx, (h_id, h_name, h_dur, h_icon, h_prog, is_done) in enumerate(habits):
        progress_pct = min(100, int((h_prog / h_dur) * 100))

        # Берем название Material иконки (если нет, ставим звездочку по умолчанию)
        icon_name = ICONS.get(h_icon, "star")

        with cols[idx % 4]:
            # 1. HTML карточки (Теперь с тегом <i> для Material Icons)
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

            # ИСПРАВЛЕНИЕ: Изменен вес колонок, чтобы "зажать" кнопки строго по центру под карточкой
            b_col_space1, b_col1, b_col2, b_col_space2 = st.columns([1, 2, 1, 1])

            with b_col1:
                if st.button("", icon=":material/calendar_month:", key=f"btn_info_{h_id}"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("SELECT log_date FROM habit_logs WHERE habit_id = ?", (h_id,))
                    hist = [r[0] for r in c.fetchall()]
                    conn.close()

                    st.session_state.open_habit_dialog = (h_id, h_name, hist)
                    st.session_state.dialog_just_opened = True
                    st.rerun()

            with b_col2:
                if not is_done:
                    if st.button("", icon=":material/check_circle:", key=f"btn_check_{h_id}"):
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("INSERT OR IGNORE INTO habit_logs (habit_id, log_date) VALUES (?, ?)",
                                  (h_id, date.today().isoformat()))
                        conn.commit()
                        conn.close()
                        st.rerun()
                else:
                    st.button("", icon=":material/task_alt:", key=f"btn_done_{h_id}", disabled=True)

else:
    st.write("---")
    st.info("Привычек пока нет. Самое время начать что-то новое!")
