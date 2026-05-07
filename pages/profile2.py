import streamlit as st
import sqlite3
import bcrypt

# ---------------- 1. КОНФИГУРАЦИЯ ----------------
st.set_page_config(page_title="Profile", layout="wide", initial_sidebar_state="expanded")

# --- ИНИЦИАЛИЗАЦИЯ ФЛАГОВ В СЕССИИ ---
if "user" not in st.session_state:
    st.session_state.user = None

if "auth_modal_triggered" not in st.session_state:
    st.session_state.auth_modal_triggered = False


def get_db_connection():
    return sqlite3.connect('treker_bd.db', check_same_thread=False)


def init_user_db():
    # Устанавливаем соединение с твоей БД
    conn = sqlite3.connect('treker_bd.db', check_same_thread=False)
    c = conn.cursor()

    # Запрос на создание таблицы user
    c.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Вызов функции при старте приложения
init_user_db()

def grant_achievement(user_id, ach_name):
    conn = sqlite3.connect('treker_bd.db', check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS user_achievements (user_id INTEGER, achievement_name TEXT, PRIMARY KEY (user_id, achievement_name))")
    conn.execute("INSERT OR IGNORE INTO user_achievements (user_id, achievement_name) VALUES (?, ?)", (user_id, ach_name))
    conn.commit()
    conn.close()

def load_settings(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS user_settings (user_id INTEGER PRIMARY KEY, week_start TEXT DEFAULT 'Понедельник', font_size TEXT DEFAULT 'Средний')")
    settings = c.execute("SELECT week_start, font_size FROM user_settings WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return settings if settings else ('Понедельник', 'Средний')


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def img_to_base64(path):
    import base64
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img3 = img_to_base64("styles/love.jpg")

st.markdown(f"""
<style>
.bg-img {{
    position: fixed;
    bottom: 45px;
    z-index: 0;
    pointer-events: none;
}}

.bg-img {{
    right: 95px;
    width: 230px;
}}
</style>

<img class="bg-img bg-right" src="data:image/jpeg;base64,{img3}">
""", unsafe_allow_html=True)

# ---------------- 2. СТИЛИ (CSS) - ТВОИ ОРИГИНАЛЬНЫЕ РАЗМЕРЫ И РАССТОЯНИЯ ----------------
st.markdown("""
<style>
    /* --- ОСНОВНЫЕ СТИЛИ ПРОФИЛЯ --- */
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
    [data-testid="stSidebar"] .stPageLink a p { display: none !important; }
    [data-testid="stSidebar"] .stPageLink a[aria-current="page"] { background-color: #FF1493 !important; }

    [data-testid="stSidebar"] .stPageLink a svg,
    [data-testid="stSidebar"] .stPageLink a i,
    [data-testid="stSidebar"] .stPageLink a span[translate="no"] {
        font-size: 35px !important; width: 35px !important; height: 35px !important;
        line-height: 35px !important; margin: 0 !important; padding: 0 !important;
        display: block !important; fill: white !important; color: white !important;
    }

    [data-testid="stSidebar"] .stPageLink a:hover {
        background-color: #70869d !important;
        transform: scale(1.05);
    }

    .profile-container {
        background: #ffffff; padding: 40px 20px; border-radius: 30px;
        text-align: center; border: 1px solid #e0e6ed; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .profile-avatar {
        width: 100px; height: 100px; margin: 0 auto 20px;
        background: linear-gradient(135deg, #5B8DBE, #4a7aa3);
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        color: white; font-size: 42px; font-weight: bold;
        box-shadow: 0 4px 10px rgba(91, 141, 190, 0.3);
    }
    .user-name { font-size: 24px; font-weight: 800; color: #334455; margin-bottom: 5px; }
    .user-mail { font-size: 14px; color: #8899aa; margin-bottom: 25px; }

    .ach-section-title { font-size: 24px; font-weight: 700; color: #334455; margin-bottom: 25px; }
    .ach-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 20px; }

    .ach-card {
        background: white; border-radius: 24px; padding: 25px 15px;
        text-align: center; transition: 0.3s; min-height: 220px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }

    .ach-icon-box { margin-bottom: 15px; }
    .ach-icon-box .material-icons { font-size: 55px; }

    .ach-name { font-size: 16px; font-weight: 800; color: #1A1C1F; margin-bottom: 8px; }

    .ach-desc {
        font-size: 12px; color: #445566 !important; font-weight: 500;
        line-height: 1.3; margin-top: 5px; min-height: 32px;
        display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
        overflow: hidden; text-overflow: ellipsis;
    }

    .locked { filter: grayscale(100%); opacity: 0.8; border: 4px dashed #ced4da; }
    .unlocked { border: 2px solid #4A90E2; box-shadow: 0 8px 20px rgba(74, 144, 226, 0.38); }

    .progress-tag {
        margin-top: 15px; font-size: 11px; font-weight: 700;
        background: #f0f2f6; padding: 4px 10px; border-radius: 12px; color: #334455;
    }

    button[kind="primary"], 
    [data-testid="stBaseButton-primary"],
    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #5B8DBE, #4a7aa3) !important;
        border: none !important;
        border-radius: 16px !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(91, 141, 190, 0.25) !important;
        transition: all 0.3s ease !important;
        height: auto !important;
        padding: 10px 20px !important;
    }

/* Tabs */
[data-baseweb="tab-highlight"] { background-color: #5B8DBE !important; }
button[data-baseweb="tab"] div { color: #8fa4bc !important; }
button[data-baseweb="tab"][aria-selected="true"] div { color: #5B8DBE !important; }

/* Inputs */
[data-baseweb="input"] { border-radius: 12px !important; }
[data-baseweb="base-input"]:focus-within, [data-baseweb="input"]:focus-within {
    border-color: #5B8DBE !important;
    box-shadow: 0 0 0 1px #5B8DBE !important;
}

.stButton > button {
    background-color: #6B7B94 !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: 600 !important;
    transition: 0.2s ease;
}

</style>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
""", unsafe_allow_html=True)


# ---------------- 3. МОДАЛЬНОЕ ОКНО ----------------
@st.dialog("Добро пожаловать")
def auth_modal():
    t1, t2 = st.tabs(["Вход", "Регистрация"])
    with t1:
        with st.form("login_form", clear_on_submit=False, border=False):
            l = st.text_input("Логин", key="login_val", placeholder="Введите логин")
            p = st.text_input("Пароль", type="password", key="pass_val", placeholder="Введите пароль")
            st.write("")
            if st.form_submit_button("Войти", use_container_width=True, type="primary"):
                conn = get_db_connection()
                res = conn.cursor().execute("SELECT id, password FROM user WHERE login=?", (l.strip(),)).fetchone()
                conn.close()
                if res and check_password(p, res[1]):
                    st.session_state.user = {"id": res[0], "nick": l.strip(), "contact": "user@example.com"}
                    st.rerun()
                else:
                    st.error("Ошибка входа")

    with t2:
        with st.form("reg_form", border=False):
            nick = st.text_input("Логин", key="reg_nick", placeholder="Придумайте логин")
            contact_beauty = st.text_input("Почта", key="reg_contact", placeholder="example@mail.com")
            p1 = st.text_input("Пароль", type="password", key="reg_p1", placeholder="Минимум 6 символов")
            p2 = st.text_input("Повторите пароль", type="password", key="reg_p2", placeholder="Пароли должны совпадать")
            st.write("")
            if st.form_submit_button("Зарегистрироваться", use_container_width=True, type="primary"):
                if not all([nick.strip(), contact_beauty.strip(), p1.strip(), p2.strip()]):
                    st.error("Заполни все поля")
                elif p1 != p2:
                    st.error("Пароли не совпадают")
                else:
                    conn = get_db_connection()
                    try:
                        cursor = conn.cursor()  # Создаем ОДИН курсор для всех операций
                        hashed = hash_password(p1)
                        cursor.execute("INSERT INTO user (login, password) VALUES (?, ?)",
                                       (nick.strip(), hashed))
                        new_id = cursor.lastrowid  # Берем ID у того же курсора
                        conn.commit()

                        # Теперь new_id точно будет числом
                        st.session_state.user = {
                            "id": new_id,
                            "nick": nick.strip(),
                            "contact": contact_beauty.strip()
                        }
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Этот логин уже занят")
                    finally:
                        conn.close()


# ---------------- 4. САЙДБАР ----------------
with st.sidebar:
    st.markdown('<div class="nav-tile"><i class="material-icons" style="font-size:40px;">menu</i></div>',
                unsafe_allow_html=True)
    st.page_link("app.py", label="Home", icon=":material/home:")
    st.page_link("pages/profile2.py", label="Profile", icon=":material/person:")
    st.page_link("pages/settings2.py", label="Settings", icon=":material/settings:")
    st.page_link("pages/contacts2.py", label="Chat", icon=":material/chat:")

# ---------------- 5. ОСНОВНОЙ КОНТЕНТ ----------------
if st.session_state.user:
    u = st.session_state.user
    _ = load_settings(u['id'])

    conn = get_db_connection()
    c = conn.cursor()

    # Инициализация таблицы кастомных ачивок, если ее нет
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_achievements (
            user_id INTEGER,
            achievement_name TEXT,
            PRIMARY KEY (user_id, achievement_name)
        )
    """)
    conn.commit()

    # Получение базовой статистики
    h_count = c.execute("SELECT COUNT(*) FROM habits WHERE user_id=?", (u['id'],)).fetchone()[0]
    l_count = c.execute("SELECT COUNT(*) FROM habit_logs l JOIN habits h ON l.habit_id=h.id WHERE h.user_id=?",
                        (u['id'],)).fetchone()[0]

    # Получение кастомных ачивок
    user_special_ach = [row[0] for row in c.execute("SELECT achievement_name FROM user_achievements WHERE user_id=?",
                                                    (u['id'],)).fetchall()]
    conn.close()

    # Проверка получения кастомных ачивок
    is_poor = 1 if "Смерть в нищете" in user_special_ach else 0
    is_samohvalov = 1 if "Самохвалов" in user_special_ach else 0
    is_air_king = 1 if "Король воздуха" in user_special_ach else 0

    achievements = [
        {"icon": "luggage", "name": "Бипки", "desc": "Что такое бипки?<br>Зарегистрироваться", "req": 0,
         "cur": h_count},
        {"icon": "wind_power", "name": "Воздух", "desc": "Что-то подуло<br>Вы выполнили первую привычку", "req": 1,
         "cur": l_count},
        {"icon": "lyrics", "name": "Оксимирон", "desc": "Ты выполнила задание на 5+<br>Вы создали пять привычек",
         "req": 5, "cur": l_count},
        {"icon": "family_restroom", "name": "Форсаж", "desc": "Последний заезд<br>Вы создали десять привычек",
         "req": 10, "cur": h_count},
        # Кастомные ачивки: требуемое значение 1, текущее 1 (если получено) или 0 (если не получено)
        {"icon": "self_improvement", "name": "Смерть в нищете", "desc": "принять/принять<br>Задонатить создателям",
         "req": 1, "cur": is_poor},
        {"icon": "accessible_forward", "name": "Самохвалов", "desc": "Почему?<br>Экспортировать", "req": 1,
         "cur": is_samohvalov},
    ]

    col_left, col_right = st.columns([1, 2.5], gap="large")

    with col_left:
        st.markdown(
            f'<div class="profile-container"><div class="profile-avatar">{u["nick"][0].upper()}</div><div class="user-name">{u["nick"]}</div><div class="user-mail">{u["contact"]}</div></div>',
            unsafe_allow_html=True)
        st.write("")
        if st.button("Выйти из аккаунта", use_container_width=True, key="logout"):
            st.session_state.user = None
            st.session_state.auth_modal_triggered = False
            st.rerun()

    with col_right:
        st.markdown('<div class="ach-section-title">Достижения</div>', unsafe_allow_html=True)
        grid_cols = st.columns(3)
        for i, ach in enumerate(achievements):
            is_open = ach['cur'] >= ach['req'] if ach['req'] > 0 else True  # Учитываем первую ачивку с req=0

            # Логика отображения тега прогресса
            # Для "Бипки" req=0, поэтому выводим 1/1 вручную. Для остальных считаем min.
            display_cur = 1 if ach['name'] == "Бипки" else min(ach['cur'], ach['req'])
            display_req = 1 if ach['name'] == "Бипки" else ach['req']

            with grid_cols[i % 3]:
                st.markdown(f"""
                <div class="ach-card {"unlocked" if is_open else "locked"}">
                <div class="ach-icon-box"><i class="material-icons" style="color: {"#4A90E2" if is_open else "#adb5bd"};">{ach['icon']}</i></div>
                <div class="ach-name">{ach['name']}</div>
                <div class="ach-desc">{ach['desc']}</div>
                <div class="progress-tag">{display_cur} / {display_req}</div>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
else:
    if not st.session_state.auth_modal_triggered:
        st.session_state.auth_modal_triggered = True
        auth_modal()
    st.markdown('<div class="auth-container-wrapper"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown(
            "<h3 style='text-align: center; color: #334455; margin-bottom: 20px;'>Войдите, чтобы увидеть профиль</h3>",
            unsafe_allow_html=True)
        if st.button("Войти или Зарегистрироваться", use_container_width=True, type="primary", key="main_auth"):
            auth_modal()
