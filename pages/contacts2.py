import streamlit as st
import sqlite3
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Контакты", layout="wide", initial_sidebar_state="expanded")

# Инициализация сессии
if "user" not in st.session_state:
    st.session_state.user = None


def grant_achievement(user_id, ach_name):
    try:
        conn = sqlite3.connect('treker_bd.db', check_same_thread=False)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id INTEGER, 
                achievement_name TEXT, 
                PRIMARY KEY (user_id, achievement_name)
            )
        """)
        conn.execute("INSERT OR IGNORE INTO user_achievements (user_id, achievement_name) VALUES (?, ?)",
                     (user_id, ach_name))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Ошибка БД: {e}")
        return False


# --- ФУНКЦИЯ ЗАГРУЗКИ НАСТРОЕК ДЛЯ ШРИФТА ---
def load_settings(user_id):
    try:
        conn = sqlite3.connect('treker_bd.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY, 
                week_start TEXT DEFAULT 'Понедельник', 
                font_size TEXT DEFAULT 'Средний'
            )
        """)
        settings = c.execute("SELECT week_start, font_size FROM user_settings WHERE user_id=?", (user_id,)).fetchone()
        conn.close()
        return settings if settings else ('Понедельник', 'Средний')
    except Exception:
        return ('Понедельник', 'Средний')


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


img3 = img_to_base64("styles/call.png")

# --- ЛОГИКА ОПРЕДЕЛЕНИЯ РАЗМЕРА ШРИФТА ---
if st.session_state.user:
    u_id = st.session_state.user.get('id', 1)
    _, s_font = load_settings(u_id)
    f_size = "14px" if s_font == "Мелкий" else "20px" if s_font == "Крупный" else "17px"
else:
    f_size = "17px"

# ТВОИ СТИЛИ С ДИНАМИЧЕСКИМ ШРИФТОМ (КОНФЛИКТЫ ИСКЛЮЧЕНЫ)
st.markdown(f"""
<style>
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        position: relative;
    }}

    [data-testid="stVerticalBlock"] > div:first-child {{
        margin-top: -30px !important; 
    }}

    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }} 
    [data-testid="stSidebarNav"] {{display: none;}}
    section[data-testid="stSidebar"] {{ width: 150px !important; min-width: 150px !important; }}

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
    header, footer, #MainMenu {{ visibility: hidden; display: none; }}

    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    .page-header {{
        font-family: 'Tahoma' !important;
        font-size: 32px !important; 
        font-weight: 600 !important;
        color: #314357 !important; 
        text-align: center !important;
        text-transform: uppercase !important;
        margin-top: 70px !important;   
        margin-bottom: 100px !important;
    }}

    .dev-card {{
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-bottom: 40px;
    }}

    .icon-circle {{
        background-color: #4A90E2 !important;
        width: 95px;
        height: 95px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.2);
    }}

    .material-icons-custom {{
        font-family: 'Material Icons' !important;
        color: white !important;
        font-size: 48px !important;
        line-height: 1 !important;
    }}

    /* ПРИМЕНЕНИЕ ДИНАМИЧЕСКОГО ШРИФТА К КАРТОЧКАМ */
    .dev-name {{
        font-family: 'Tahoma', sans-serif !important;
        font-size: calc({f_size} + 4px) !important; /* Было 21px при базе 17px */
        font-weight: 700 !important;
        color: #2E4053 !important;
    }}

    .dev-role {{ 
        font-family: 'Tahoma', sans-serif !important; 
        font-size: calc({f_size} - 3px) !important; /* Было 14px при базе 17px */
        color: #7F8C8D !important; 
    }}

    .dev-email {{ 
        font-family: 'Tahoma', sans-serif !important; 
        font-size: calc({f_size} - 2px) !important; /* Было 15px при базе 17px */
        color: #4A90E2 !important; 
        text-decoration: none !important; 
    }}

    .img3 {{
        position: absolute;
        bottom: 400px; 
        left: 50%; 
        transform: translateX(-50%); 
        z-index: 1;
        pointer-events: none;
    }}

    .img3 img {{
        width: 185px !important;
    }}

    div.stButton {{
        display: flex !important;
        margin-left: auto !important;
        margin-right: auto !important;
        width: fit-content !important;
        margin-top: 100px !important;
    }}

    .stButton > button {{
        background-color: #8fa4bc !important; 
        color: white !important;
        padding: 12px 30px !important;
        border-radius: 20px !important; 
        text-decoration: none !important;
        font-family: 'Tahoma', sans-serif !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        border: none !important;
        display: inline-block !important;
    }}

    .stButton > button:hover {{
        background-color: #70869d !important; 
        transform: scale(1.05) !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
    }}

@media (max-width: 768px) {{


    section[data-testid="stSidebar"] {{
        width: 125px !important;
        min-width: 125px !important;
        max-width: 125px !important;
        background-color: #f8f9fa !important; /* Можно задать легкий фон для мобильной шторки */
    }}

    /* Чуть-чуть уменьшаем плитки, чтобы они идеально вписывались в узкий экран смартфона */
    .nav-tile, [data-testid="stSidebar"] .stPageLink a {{
        width: 75px !important;
        height: 75px !important;
        margin: 12px auto !important;
        border-radius: 18px !important;
    }}

    /* Пропорционально уменьшаем иконки внутри плиток */
    [data-testid="stSidebar"] .stPageLink a svg,
    [data-testid="stSidebar"] .stPageLink a i,
    [data-testid="stSidebar"] .stPageLink a span[translate="no"] {{
        font-size: 30px !important; 
        width: 30px !important;
        height: 30px !important;
        line-height: 30px !important;
    }}
    
    /* Сдвигаем контент страницы, чтобы при открытии сайдбара на мобилке ничего не ломалось */
    [data-testid="stMain"] {{
        margin-left: 0px !important;
    }}
    /* 1. Фоновые картинки (заяц, трубка) на мобилках будут перекрывать контент. Лучше их скрыть */
    .bg-img, .img3 {{
        display: none !important;
    }}

    /* 3. Кнопка "Добавить привычку" или "Поддержать" (были по 300px).
       На мобилке пусть растягиваются на всю ширину экрана для удобного тапа пальцем */
    button[id*="add_habit_btn"], .stButton > button {{
        width: 100% !important;
        max-width: 100% !important;
    }}

    /* 4. Заголовки страниц (были огромными — 32px с отступами по 100px). Сжимаем их */
    .page-header {{
        font-size: 24px !important;
        margin-top: 20px !important;
        margin-bottom: 30px !important;
    }}

    /* 5. Карточки привычек на главной. 
       Вместо фиксированных 210px сделаем их резиновыми */
    .habit-card {{
        width: 100% !important;
        max-width: 260px; /* Чтобы не были слишком гигантскими */
        margin: 0 auto 15px auto !important;
    }}
}}

</style>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown('<div class="page-header">КОНТАКТЫ</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="nav-tile"><i class="material-icons" style="font-size:40px;">menu</i></div>',
                unsafe_allow_html=True)
    st.page_link("app.py", label="Home", icon=":material/home:")
    st.page_link("pages/profile2.py", label="Profile", icon=":material/person:")
    st.page_link("pages/settings2.py", label="Settings", icon=":material/settings:")
    st.page_link("pages/contacts2.py", label="Chat", icon=":material/chat:")


def draw_contact(name, role, icon, email):
    st.markdown(f"""
        <div class="dev-card">
            <div class="icon-circle">
                <span class="material-icons-custom">{icon}</span>
            </div>
            <div class="dev-name">{name}</div>
            <div class="dev-role">{role}</div>
            <div class="dev-email copyable-email" 
                 data-email="{email}"
                 style="cursor: pointer; transition: 0.3s;">
                {email}
            </div>
        </div>
    """, unsafe_allow_html=True)


col0, col1, col2 = st.columns(3)
with col0:
    draw_contact("Самохвалов Семен", "Разработчик", "face", "scpsosat837@gmail.com")

with col2:
    draw_contact("Кис Анна", "Разработчик", "face_2", "a-kisanna@yandex.ru")
st.markdown("<br>", unsafe_allow_html=True)
col3, col4, col5 = st.columns(3)
with col3:
    draw_contact("Еганова Анастасия", "Менеджер команды", "face_4", "eganova.nastyaa@gmail.com")
with col4:
    draw_contact("Рябинина Ирина", "Дизайнер", "face_3", "irina_ryabinina2007@mail.ru")
with col5:
    draw_contact("Григорян Нарек", "Дизайнер", "face_6", "narek02112020@gmail.com")

if st.session_state.user:
    _, center_col, _ = st.columns([1, 2, 1])

    with center_col:
        if st.button("Поддержать создателей", use_container_width=True):
            u_id = st.session_state.user.get('id')
            if u_id:
                grant_achievement(u_id, "Смерть в нищете")

            js_click = """
            <script>
                window.parent.open("https://messenger.online.sberbank.ru/sl/8JxgkasHxxoOHS3Rh", "_blank");
            </script>
            """
            components.html(js_click, height=0, width=0)
else:
    st.info("Войдите в систему для получения достижений")

# Картинка с зайцем/телефоном снизу
st.markdown(f"""
    <div class="img3">
        <img src="data:image/png;base64,{img3}">
    </div>
""", unsafe_allow_html=True)

# Скрипт только для копирования почты
js_code = """
<script>
    const parentDoc = window.parent.document;
    function attachClipboardEvents() {
        const emails = parentDoc.querySelectorAll('.copyable-email:not(.js-bound)');
        emails.forEach(el => {
            el.classList.add('js-bound'); 
            el.addEventListener('click', function() {
                const emailText = this.getAttribute('data-email');
                if (window.parent.navigator.clipboard) {
                    window.parent.navigator.clipboard.writeText(emailText).then(() => {
                        this.innerText = 'Скопировано!';
                        setTimeout(() => { this.innerText = emailText; }, 1500);
                    });
                }
            });
        });
    }
    setInterval(attachClipboardEvents, 500);
</script>
"""
components.html(js_code, height=0, width=0)
