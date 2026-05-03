import streamlit as st
import sqlite3
import os

# ---------------- 1. КОНФИГУРАЦИЯ ----------------
st.set_page_config(page_title="Настройки", layout="wide", initial_sidebar_state="expanded")

if "user" not in st.session_state:
    st.session_state.user = None

def get_db_connection():
    return sqlite3.connect('treker_bd.db', check_same_thread=False)

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

# Получение настроек пользователя (возвращает 2 значения)
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

# ---------------- 2. ПРИМЕНЕНИЕ ШРИФТА (CSS) ----------------
if st.session_state.user:
    # ИСПРАВЛЕНО: Распаковываем 2 значения, а не 3
    current_week, current_font = load_settings(st.session_state.user['id'])

    font_css = ""
    if current_font == "Мелкий":
        font_css = "html, body, p, div, span, label { font-size: 14px !important; }"
    elif current_font == "Крупный":
        font_css = "html, body, p, div, span, label { font-size: 18px !important; }"

    if font_css:
        st.markdown(f"<style>{font_css}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
/* --- НАВИГАЦИЯ (САЙДБАР) --- */
    [data-testid="stHeader"] { background: rgba(0,0,0,0); } 
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
    header, footer, #MainMenu { visibility: hidden; display: none; }

    .page-title { text-align: center; margin: 30px 0; font-size: 32px; font-weight: 700; color: #334455; }
    .settings-section { background: white; padding: 25px; border-radius: 20px; border: 1px solid #E0E6ED; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
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

# ---------------- 4. ПРОВЕРКА АВТОРИЗАЦИИ ----------------
st.markdown('<div class="page-title">НАСТРОЙКИ</div>', unsafe_allow_html=True)

if not st.session_state.get("user"):
    st.warning("Войдите в аккаунт для доступа к настройкам.")
    st.stop()

user_id = st.session_state.user['id']

# ---------------- 5. ДИАЛОГИ И ФУНКЦИИ ----------------
@st.dialog("⚠️ Сброс привычек")
def confirm_reset():
    st.write("Вы уверены, что хотите удалить **все привычки и прогресс**? Это действие нельзя отменить.")
    if st.button("Да, удалить всё", type="primary", use_container_width=True):
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
    <head>
        <meta charset='utf-8'>
        <title>Экспорт привычек</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; color: #334455; }}
            h1 {{ color: #4A90E2; border-bottom: 2px solid #E0E6ED; padding-bottom: 10px; }}
            h3 {{ color: #111111; margin-top: 30px; }}
            ul {{ background: #f8f9fa; padding: 20px 40px; border-radius: 12px; }}
            li {{ margin-bottom: 5px; }}
        </style>
    </head>
    <body>
        <h1>📊 Отчет по привычкам: {username}</h1>
    """

    if not habits:
        html += "<p>У вас пока нет добавленных привычек.</p>"

    for h_id, h_name in habits:
        logs = c.execute("SELECT log_date FROM habit_logs WHERE habit_id=? ORDER BY log_date", (h_id,)).fetchall()
        html += f"<h3>🎯 {h_name}</h3><ul>"
        if logs:
            for log in logs:
                html += f"<li>Выполнено: {log[0]}</li>"
        else:
            html += "<li><i>Отметок пока нет</i></li>"
        html += "</ul>"

    html += "</body></html>"
    conn.close()
    return html

# ---------------- 6. ОСНОВНОЙ КОНТЕНТ НАСТРОЕК ----------------

# ИСПРАВЛЕНО: Убран skip_double, теперь принимаем только 2 значения
week_start, font_size = load_settings(user_id)

col1, col2 = st.columns([1.5, 1], gap="large")

with col1:
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.subheader("⚙️ Внешний вид и поведение")

    font_options = ["Мелкий", "Средний", "Крупный"]
    safe_font_value = font_size if font_size in font_options else "Средний"

    new_font = st.select_slider(
        "Размер шрифта",
        options=font_options,
        value=safe_font_value
    )

    new_week = st.radio(
        "Начало недели",
        ["Понедельник", "Воскресенье"],
        index=0 if week_start == "Понедельник" else 1,
        horizontal=True
    )

    if st.button("Сохранить изменения", type="primary"):
        conn = get_db_connection()
        conn.execute("""
            UPDATE user_settings 
            SET week_start=?, font_size=? 
            WHERE user_id=?
        """, (new_week, new_font, user_id))
        conn.commit()
        conn.close()
        st.success("Настройки успешно сохранены!")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.subheader("📄 Экспорт данных")
    st.write("Сохраните историю своих привычек в удобном формате.")

    html_data = generate_html_report(user_id, st.session_state.user.get('nick', 'Пользователь'))

    st.download_button(
        label="Экспорт в HTML",
        data=html_data,
        file_name="Habits_Report.html",
        mime="text/html",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="settings-section" style="border-color: #ff4b4b;">', unsafe_allow_html=True)
    st.subheader("🚨 Опасная зона")
    st.write("Сброс полностью удалит все ваши привычки и историю их выполнения.")

    if st.button("Сбросить все привычки", use_container_width=True):
        confirm_reset()

    st.markdown('</div>', unsafe_allow_html=True)
