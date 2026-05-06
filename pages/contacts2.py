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
        conn.execute("INSERT OR IGNORE INTO user_achievements (user_id, achievement_name) VALUES (?, ?)", (user_id, ach_name))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Ошибка БД: {e}")
        return False



def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img3 = img_to_base64("styles/call.png")

# ТВОИ СТИЛИ + ДОБАВЛЕНО СОКРЫТИЕ ЧЕКБОКСА
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        position: relative;
    }

    [data-testid="stVerticalBlock"] > div:first-child {
        margin-top: -30px !important; 
    }

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

    [data-testid="stSidebar"] .stPageLink a div {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [data-testid="stSidebar"] .stPageLink a p {
        display: none !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 0 !important;
        height: 0 !important;
    }

    [data-testid="stSidebar"] .stPageLink a[aria-current="page"] { 
        background-color: #FF1493 !important; 
    }

    [data-testid="stSidebar"] .stPageLink a svg,
    [data-testid="stSidebar"] .stPageLink a i,
    [data-testid="stSidebar"] .stPageLink a span[translate="no"] {
        font-size: 35px !important; 
        width: 35px !important;
        height: 35px !important;
        line-height: 35px !important;
        margin: 0 !important; 
        padding: 0 !important;
        display: block !important;
        fill: white !important; 
        color: white !important; 
    }

    [data-testid="stSidebar"] .stPageLink a:hover {
        background-color: #70869d !important;
        transform: scale(1.05);
    }
    header, footer, #MainMenu { visibility: hidden; display: none; }

    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    .page-header {
        font-family: 'Tahoma' !important;
        font-size: 32px !important; 
        font-weight: 600 !important;
        color: #314357 !important; 
        text-align: center !important;
        text-transform: uppercase !important;
        margin-top: 70px !important;   
        margin-bottom: 100px !important;
    }

    .dev-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-bottom: 40px;
    }

    .icon-circle {
        background-color: #4A90E2 !important;
        width: 95px;
        height: 95px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.2);
    }

    .material-icons-custom {
        font-family: 'Material Icons' !important;
        color: white !important;
        font-size: 48px !important;
        line-height: 1 !important;
    }

    .dev-name {
        font-family: 'Tahoma', sans-serif !important;
        font-size: 21px !important;
        font-weight: 700 !important;
        color: #2E4053 !important;
    }

    .dev-role { font-family: 'Tahoma', sans-serif; font-size: 14px; color: #7F8C8D; }
    .dev-email { font-family: 'Tahoma', sans-serif; font-size: 15px; color: #4A90E2; text-decoration: none; }


    .img3 {
        position: absolute;
        bottom: 400px; 
        left: 50%; 
        transform: translateX(-50%); 
        z-index: 1;
        pointer-events: none;
    }

    .img3 img {
        width: 185px !important;
    }
    
    /* Находим контейнер кнопки и заставляем его центровать содержимое */
    div.stButton {
        display: flex !important;
        margin-left: auto !important;
        margin-right: auto !important;
        width: fit-content !important;
        margin-top: 100px !important;
    }

    /* Сама кнопка */
    .stButton > button {
        background-color: #8fa4bc !important; /* Цвет как у сайдбара */
        color: white !important;
        padding: 12px 30px !important;
        border-radius: 20px !important; /* Скругление как у плиток */
        text-decoration: none !important;
        font-family: 'Tahoma', sans-serif !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        border: none !important;
        display: inline-block !important;
    }

    .stButton > button:hover {
        background-color: #70869d !important; /* Цвет ховера как у сайдбара */
        transform: scale(1.05) !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
    }

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


# 1. Твоя кнопка чистым HTML/CSS. Без тега скрипта внутри (перенесли его в общий JS)
if st.session_state.user:
    # Создаем 3 колонки, средняя будет для кнопки
    # Соотношение 1:2:1 или 1:1:1 поможет выровнять точно по центру
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
