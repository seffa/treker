import streamlit as st
import sqlite3
import bcrypt

# ---------------- 1. КОНФИГУРАЦИЯ ----------------
st.set_page_config(page_title="Profile", layout="wide", initial_sidebar_state="expanded")


def get_db_connection():
    return sqlite3.connect('treker_bd.db', check_same_thread=False)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# ---------------- 2. СТИЛИ (CSS) ----------------
st.markdown("""
<style>
    /* --- НАВИГАЦИЯ (САЙДБАР) --- */
    [data-testid="stSidebarNav"] {display: none;}
    section[data-testid="stSidebar"] { width: 150px !important; min-width: 150px !important; }
    .nav-tile, [data-testid="stSidebar"] .stPageLink a {
        display: flex !important; align-items: center !important; justify-content: center !important;
        width: 85px !important; height: 85px !important; margin: 15px auto !important;
        border-radius: 20px !important; background-color: #8fa4bc !important;
        transition: all 0.3s ease !important; text-decoration: none !important;

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
    }
    /* --- ЛЕВАЯ ПАНЕЛЬ (ПРОФИЛЬ) --- */
    .profile-container {
        background: #ffffff;
        padding: 40px 20px;
        border-radius: 30px;
        text-align: center;
        border: 1px solid #e0e6ed;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
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

    /* --- ПРАВАЯ ПАНЕЛЬ (ДОСТИЖЕНИЯ) --- */
    .ach-section-title { font-size: 24px; font-weight: 700; color: #334455; margin-bottom: 25px; }
    .ach-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 20px; }

    .ach-card {
        background: white; border-radius: 24px; padding: 25px 15px;
        text-align: center; transition: 0.3s; min-height: 220px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }

    .ach-icon-box { margin-bottom: 15px; }
    .ach-icon-box .material-icons { font-size: 55px; }

    /* Текст достижений */
    .ach-name { font-size: 16px; font-weight: 800; color: #1A1C1F; margin-bottom: 8px; }

    /* ИСПРАВЛЕННЫЙ ЦВЕТ ОПИСАНИЯ (Темный и контрастный) */
    .ach-desc { 
        font-size: 12px; 
        color: #445566 !important; 
        font-weight: 500;
        line-height: 1.4; 
    }

    .locked { filter: grayscale(100%); opacity: 0.4; border: 2px dashed #ced4da; }
    .unlocked { border: 2px solid #AFEEEE; box-shadow: 0 8px 20px rgba(70, 130, 180, 0.1); }

    .progress-tag {
        margin-top: 15px; font-size: 11px; font-weight: 700;
        background: #f0f2f6; padding: 4px 10px; border-radius: 12px; color: #334455;
    }

    /* Кнопка входа */
    .auth-btn-container { color: #334455; text-align: center; margin-top: 100px; }
</style>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
""", unsafe_allow_html=True)


# ---------------- 3. МОДАЛЬНОЕ ОКНО ----------------
@st.dialog("Вход в систему")
def auth_modal():
    t1, t2 = st.tabs(["Вход", "Регистрация"])

    with t1:
        # Оборачиваем в форму для работы Enter
        with st.form("login_form", clear_on_submit=False, border=False):
            l = st.text_input("Логин", key="login_val")
            p = st.text_input("Пароль", type="password", key="pass_val")
            submit_login = st.form_submit_button("Войти", use_container_width=True, type="primary")

            if submit_login:
                conn = get_db_connection()
                res = conn.cursor().execute("SELECT id, password FROM user WHERE login=?", (l.strip(),)).fetchone()
                conn.close()
                if res and check_password(p, res[1]):
                    st.session_state.user = {"id": res[0], "nick": l.strip(), "contact": "user@example.com"}
                    st.rerun()
                else:
                    st.error("Ошибка входа")

    with t2:
        # Оборачиваем в форму для работы Enter
        with st.form("reg_form", border=False):
            nick = st.text_input("Логин", key="reg_nick")
            contact_beauty = st.text_input("Почта", key="reg_contact")
            p1 = st.text_input("Пароль", type="password", key="reg_p1")
            p2 = st.text_input("Повтори пароль", type="password", key="reg_p2")
            submit_reg = st.form_submit_button("Зарегистрироваться", use_container_width=True, type="primary")

            if submit_reg:
                if not all([nick.strip(), contact_beauty.strip(), p1.strip(), p2.strip()]):
                    st.error("Заполни все поля")
                elif p1 != p2:
                    st.error("Пароли не совпадают")
                else:
                    conn = get_db_connection()
                    c = conn.cursor()
                    try:
                        hashed = hash_password(p1)
                        c.execute("INSERT INTO user (login, password) VALUES (?, ?)", (nick.strip(), hashed))
                        new_id = c.lastrowid
                        conn.commit()
                        st.session_state.user = {"id": new_id, "nick": nick.strip(), "contact": contact_beauty.strip()}
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

if "user" not in st.session_state:
    st.session_state.user= None

if st.session_state.user:
    u = st.session_state.user

    # Получаем данные прогресса
    conn = get_db_connection()
    c = conn.cursor()
    h_count = c.execute("SELECT COUNT(*) FROM habits WHERE user_id=?", (u['id'],)).fetchone()[0]
    l_count = c.execute("SELECT COUNT(*) FROM habit_logs l JOIN habits h ON l.habit_id=h.id WHERE h.user_id=?",
                        (u['id'],)).fetchone()[0]
    conn.close()

    # Список достижений (Только Material Icons)
    # Названия иконок можно брать тут: https://fonts.google.com/icons
    achievements = [
        {"icon": "auto_awesome", "name": "Первооткрыватель", "desc": "Создана 1-я полезная привычка", "req": 1,
         "cur": h_count},
        {"icon": "local_fire_department", "name": "В ударе", "desc": "Выполнил 5 задач из списка", "req": 5,
         "cur": l_count},
        {"icon": "workspace_premium", "name": "Коллекционер", "desc": "У тебя уже 10 активных целей", "req": 10,
         "cur": h_count},
        {"icon": "military_tech", "name": "Железная воля", "desc": "50 отметок в твоем журнале", "req": 50,
         "cur": l_count},
        {"icon": "stars", "name": "Триатлон", "desc": "3 привычки одновременно", "req": 3, "cur": h_count},
        {"icon": "emoji_events", "name": "Чемпион", "desc": "Достигнут рубеж в 20 отметок", "req": 20, "cur": l_count}
    ]

    col_left, col_right = st.columns([1, 2.5], gap="large")

    with col_left:
        st.markdown(f"""
        <div class="profile-container">
            <div class="profile-avatar">{u['nick'][0].upper()}</div>
            <div class="user-name">{u['nick']}</div>
            <div class="user-mail">{u['contact']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("Выйти из аккаунта", use_container_width=True, key="logout"):
            st.session_state.user = None
            st.rerun()

    with col_right:
        st.markdown('<div class="ach-section-title">Достижения</div>', unsafe_allow_html=True)

        # Сетка достижений
        st.markdown('<div class="ach-grid">', unsafe_allow_html=True)
        grid_cols = st.columns(3)

        for i, ach in enumerate(achievements):
            is_open = ach['cur'] >= ach['req']
            status_class = "unlocked" if is_open else "locked"
            icon_color = "#ADD8E6" if is_open else "#adb5bd"

            with grid_cols[i % 3]:
                st.markdown(f"""
                <div class="ach-card {status_class}">
                    <div class="ach-icon-box">
                        <i class="material-icons" style="color: {icon_color};">{ach['icon']}</i>
                    </div>
                    <div class="ach-name">{ach['name']}</div>
                    <div class="ach-desc">{ach['desc']}</div>
                    <div class="progress-tag">{min(ach['cur'], ach['req'])} / {ach['req']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # Если не залогинен
    st.markdown('<div class="auth-btn-container">', unsafe_allow_html=True)
    if st.button("Войти в профиль", use_container_width=False, type="secondary", key="main_auth"):
        auth_modal()
    st.markdown('</div>', unsafe_allow_html=True)
