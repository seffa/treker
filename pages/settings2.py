import streamlit as st
import sqlite3
import os

# ---------------- 1. КОНФИГУРАЦИЯ ----------------
st.set_page_config(page_title="Настройки", layout="wide", initial_sidebar_state="expanded")

if "user" not in st.session_state:
    st.session_state.user = None

def grant_achievement(user_id, ach_name):
    conn = sqlite3.connect('treker_bd.db', check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS user_achievements (user_id INTEGER, achievement_name TEXT, PRIMARY KEY (user_id, achievement_name))")
    conn.execute("INSERT OR IGNORE INTO user_achievements (user_id, achievement_name) VALUES (?, ?)", (user_id, ach_name))
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('treker_bd.db', check_same_thread=False)

def on_export_click():
    if st.session_state.user:
        grant_achievement(st.session_state.user['id'], "Самохвалов")

# Инициализация таблицы настроек
def init_settings_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            week_start TEXT DEFAULT 'Понедельник',
            font_size TEXT DEFAULT 'Средний'
        )
    """)
    conn.commit()
    conn.close()


init_settings_db()


# Получение настроек пользователя
def load_settings(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    settings = c.execute("SELECT week_start, font_size FROM user_settings WHERE user_id=?",
                         (user_id,)).fetchone()
    if not settings:
        c.execute("INSERT INTO user_settings (user_id) VALUES (?)", (user_id,))
        conn.commit()
        settings = ('Понедельник', 'Средний')
    conn.close()
    return settings


# ---------------- 2. ПРИМЕНЕНИЕ ШРИФТА И ЦВЕТОВ (CSS) ----------------
if st.session_state.user:
    current_week, current_font = load_settings(st.session_state.user['id'])

    if current_font == "Мелкий":
        base_size, h_size = "14px", "24px"
    elif current_font == "Крупный":
        base_size, h_size = "20px", "36px"
    else:
        base_size, h_size = "16px", "28px"

    font_css = f"""
            <style>
                .block-container {{
                    padding-top: 2rem !important;
                    padding-bottom: 0rem !important;
                    position: relative;
                }}
            
                .page-title {{ 
                    text-align: center; margin-bottom: 80px !important; 
                    font-size: {h_size} !important; font-weight: 700; color: #334455; 
                }}

                html, body, [data-testid="stWidgetLabel"] p, .stMarkdown p, 
                .stButton button, .stDownloadButton button, .stSelectbox div, 
                .stSlider div, .stRadio label, .stTextInput input, label {{
                    font-size: {base_size} !important;
                }}

                div[data-testid="stTickBar"] {{ display: none !important; }}

                /* --- ТЕ САМЫЕ ЗАКРУГЛЕННЫЕ КНОПКИ --- */
                .stButton button, .stDownloadButton button {{
                    border-radius: 10px !important; /* Овальные */
                    width: fit-content !important;  /* Не на всю ширину */
                    min-width: 220px !important;    /* Но солидные */
                    margin: 0 auto !important;      /* Центровка */
                    display: block !important;
                    padding: 0.6rem 2.5rem !important;
                    font-weight: 600 !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    border: none !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.5px !important;
                }}

                .stButton button:active, .stDownloadButton button:active {{
                    transform: scale(0.95) !important;
                }}

                /* ЦВЕТ: СОХРАНИТЬ (PRIMARY) */
                button[kind="primary"] {{
                    background: linear-gradient(135deg, #5B8DBE 0%, #3a6a99 100%) !important;
                    color: white !important;
                    box-shadow: 0 4px 15px rgba(91, 141, 190, 0.4) !important;
                }}
                button[kind="primary"]:hover {{
                    box-shadow: 0 6px 20px rgba(91, 141, 190, 0.6) !important;
                    transform: translateY(-2px);
                }}

                /* ЦВЕТ: ЭКСПОРТ (DOWNLOAD) */
                .stDownloadButton button {{
                    background: linear-gradient(135deg, #ffffff 0%, #f0f4f8 100%) !important;
                    color: #5B8DBE !important;
                    border: 1px solid #5B8DBE !important;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
                }}
                .stDownloadButton button:hover {{
                    background: #5B8DBE !important;
                    color: white !important;
                    box-shadow: 0 6px 15px rgba(91, 141, 190, 0.3) !important;
                }}

                /* ЦВЕТ: СБРОСИТЬ (DANGER) */
                div.stButton > button:not([kind="primary"]) {{
                    background: linear-gradient(135deg, #ff4b4b 0%, #d62d2d 100%) !important;
                    color: white !important;
                    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3) !important;
                }}
                div.stButton > button:not([kind="primary"]):hover {{
                    box-shadow: 0 6px 20px rgba(255, 75, 75, 0.5) !important;
                    transform: translateY(-2px);
                }}

                [data-testid="stSidebar"] .material-icons, 
                [data-testid="stSidebar"] svg,
                [data-testid="stSidebar"] span {{
                    font-size: 35px !important;
                }}
            </style>
            """
    st.markdown(font_css, unsafe_allow_html=True)

st.markdown("""
<style>
    /* --- НАВИГАЦИЯ (САЙДБАР) --- */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        position: relative;
    }
    
    /* ХИТРАЯ МАСКИРОВКА ХЕДЕРА: прячем фон, но оставляем нативную кнопку */
    footer, #MainMenu { visibility: hidden; display: none; }
    header[data-testid="stHeader"] { 
        visibility: hidden !important; 
        background: transparent !important;
    }
    header[data-testid="stHeader"] button { 
        visibility: visible !important; 
        color: #8fa4bc !important; 
    }

    [data-testid="stSidebarNav"] {display: none;}
    section[data-testid="stSidebar"] { width: 150px !important; min-width: 150px !important; }

    .nav-tile, [data-testid="stSidebar"] .stPageLink a {
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
    }

    [data-testid="stSidebar"] .stPageLink a div { display: flex !important; align-items: center !important; justify-content: center !important; }
    [data-testid="stSidebar"] .stPageLink a p { display: none !important; margin: 0 !important; padding: 0 !important; width: 0 !important; height: 0 !important; }
    [data-testid="stSidebar"] .stPageLink a[aria-current="page"] { background-color: #FF1493 !important; }

    [data-testid="stSidebar"] .stPageLink a svg,
    [data-testid="stSidebar"] .stPageLink a i,
    [data-testid="stSidebar"] .stPageLink a span[translate="no"] {
        font-size: 35px !important; width: 35px !important; height: 35px !important; line-height: 35px !important;
        margin: 0 !important; padding: 0 !important; display: block !important; fill: white !important; color: white !important;
    }

    [data-testid="stSidebar"] .stPageLink a:hover { background-color: #70869d !important; transform: scale(1.05); }

    .settings-section { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E0E6ED; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }

    /* Карточки настроек */
    .inner-setting-card {
        background: #ffffff;
        border: 1px solid rgba(224, 230, 237, 0.5);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03), 0 10px 15px -3px rgba(91, 141, 190, 0.05);
    }

    .inner-setting-card:hover {
        transform: translateY(-5px);
        border-color: rgba(91, 141, 190, 0.4);
        box-shadow: 0 20px 25px -5px rgba(91, 141, 190, 0.15), 0 10px 10px -5px rgba(91, 141, 190, 0.1);
    }
    
    .inner-setting-card { border: 1px solid #4A90E2; box-shadow: 0 8px 20px rgba(74, 144, 226, 0.38); }

    .section-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
    }

    .section-header i {
        background: #f0f4f8;
        padding: 8px;
        border-radius: 12px;
        color: #5B8DBE;
    }

    .section-header span {
        color: #334455;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    .setting-label {
        font-weight: 600 !important;
        color: #4A5568 !important;
        margin-bottom: 10px !important;
        display: block;
        font-size: 20px !important; 
    }

    /* -----------------------------------------------------------------
       ПОЛНЫЙ МОБИЛЬНЫЙ АДАПТИВ (МЕДИА-ЗАПРОСЫ)
       ----------------------------------------------------------------- */
    @media (max-width: 768px) {
        /* Контролируем ширину шторки сайдбара на телефонах */
        section[data-testid="stSidebar"] {
            width: 125px !important;
            min-width: 125px !important;
            max-width: 125px !important;
        }

        /* Уменьшаем квадратные плитки меню под мобильный экран */
        .nav-tile, [data-testid="stSidebar"] .stPageLink a {
            width: 75px !important;
            height: 75px !important;
            margin: 12px auto !important;
            border-radius: 18px !important;
        }

        /* Масштабируем иконки внутри плиток */
        [data-testid="stSidebar"] .stPageLink a svg,
        [data-testid="stSidebar"] .stPageLink a i,
        [data-testid="stSidebar"] .stPageLink a span[translate="no"] {
            font-size: 30px !important; 
            width: 30px !important;
            height: 30px !important;
            line-height: 30px !important;
        }

        /* Кнопки настроек и экспорта растягиваем на мобилках для удобного тапа */
        .stButton button, .stDownloadButton button {
            width: 100% !important;
            min-width: 100% !important;
        }

        /* Фиксим отступы заголовка на маленьких дисплеях */
        .page-title {
            margin-bottom: 40px !important;
        }
    }
        
</style>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
""", unsafe_allow_html=True)

# ---------------- 3. НАВИГАЦИЯ ----------------
with st.sidebar:
    st.markdown('<div class="nav-tile"><i class="material-icons" style="font-size:40px;">menu</i></div>',
                unsafe_allow_html=True)
    st.page_link("app.py", label="Home", icon=":material/home:")
    st.page_link("pages/profile2.py", label="Profile", icon=":material/person:")
    st.page_link("pages/settings2.py", label="Settings", icon=":material/settings:")
    st.page_link("pages/contacts2.py", label="Chat", icon=":material/chat:")

st.markdown('<div class="page-title">НАСТРОЙКИ</div>', unsafe_allow_html=True)

if not st.session_state.get("user"):
    st.warning("Войдите в аккаунт для доступа к настройкам.")
    st.stop()

user_id = st.session_state.user['id']


# ---------------- 4. ДИАЛОГИ И ФУНКЦИИ ----------------
@st.dialog("Сброс привычек")
def confirm_reset():
    st.write("Вы уверены, что хотите удалить **все привычки и прогресс**?")
    if st.button("Да, удалить всё", use_container_width=True):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM habit_logs WHERE habit_id IN (SELECT id FROM habits WHERE user_id=?)", (user_id,))
        c.execute("DELETE FROM habits WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        st.success("Все привычки успешно удалены.")
        st.rerun()


def generate_html_report(uid, username):
    conn = get_db_connection()
    c = conn.cursor()
    habits = c.execute("SELECT id, name FROM habits WHERE user_id=?", (uid,)).fetchall()

    html = f"""
    <html>
    <head><meta charset='utf-8'><title>Отчет</title></head>
    <body style="font-family: sans-serif; padding: 40px; color: #334455;">
        <h1>📊 Отчет по привычкам: {username}</h1>
    """
    for h_id, h_name in habits:
        logs = c.execute("SELECT log_date FROM habit_logs WHERE habit_id=? ORDER BY log_date", (h_id,)).fetchall()
        html += f"<h3>🎯 {h_name}</h3><ul>"
        if logs:
            for log in logs: html += f"<li>Выполнено: {log[0]}</li>"
        else:
            html += "<li><i>Отметок нет</i></li>"
        html += "</ul>"
    html += "</body></html>"
    conn.close()
    return html


# ---------------- 5. ОСНОВНОЙ КОНТЕНТ ----------------
week_start, font_size = load_settings(user_id)
col1, col2 = st.columns([1.5, 1], gap="large")

with col1:
    st.markdown(f"""
        <div class="inner-setting-card">
            <div class="section-header">
                <i class="material-icons" style="color: #5B8DBE;">palette</i>
                <span>Внешний вид и поведение</span>
            </div>
    """, unsafe_allow_html=True)
    st.markdown('<span class="setting-label">Управление размером текста</span>', unsafe_allow_html=True)
    font_options = ["Мелкий", "Средний", "Крупный"]
    new_font = st.select_slider("Scale", options=font_options,
                                value=font_size if font_size in font_options else "Средний",
                                label_visibility="collapsed")

    st.write("")
    st.markdown('<span class="setting-label">Начало календарной недели</span>', unsafe_allow_html=True)
    new_week = st.radio("Week", ["Понедельник", "Воскресенье"], index=0 if week_start == "Понедельник" else 1,
                        horizontal=True, label_visibility="collapsed")

    st.write("")
    if st.button("Сохранить все изменения", type="primary", use_container_width=True):
        conn = get_db_connection()
        conn.execute("UPDATE user_settings SET week_start=?, font_size=? WHERE user_id=?",
                     (new_week, new_font, user_id))
        conn.commit()
        conn.close()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="inner-setting-card report-card">
            <div class="section-header">
                <i class="material-icons" style="color: #5B8DBE;">file_download</i>
                <span>Экспорт данных</span>
            </div>
    """, unsafe_allow_html=True)
    st.write("Сохраните историю своих привычек в формате HTML.")
    html_data = generate_html_report(user_id, st.session_state.user.get('nick', 'User'))
    st.download_button(
        label="Экспорт в HTML",
        data=html_data,
        file_name="Report.html",
        mime="text/html",
        use_container_width=True,
        on_click=on_export_click
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="inner-setting-card danger-card">
            <div class="section-header">
                <i class="material-icons" style="color: #5B8DBE;">warning</i>
                <span>Опасная зона</span>
            </div>
    """, unsafe_allow_html=True)
    st.write("Сброс полностью удалит все ваши привычки и историю их выполнения.")
    if st.button("Сбросить все привычки", use_container_width=True):
        confirm_reset()
    st.markdown('</div>', unsafe_allow_html=True)
