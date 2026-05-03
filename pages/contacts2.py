import streamlit as st
import sqlite3

st.set_page_config(page_title="Контакты", layout="wide", initial_sidebar_state="expanded")

# Инициализация сессии (ДОЛЖНА БЫТЬ В САМОМ НАЧАЛЕ)
if "user" not in st.session_state:
    st.session_state.user = None


def get_db_connection():
    return sqlite3.connect('treker_bd.db', check_same_thread=False)

st.markdown("""
<style>

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* Убираем лишние пустые блоки сверху */
    [data-testid="stVerticalBlock"] > div:first-child {
        margin-top: -30px !important; 
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
    
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
    
    .page-header {
        font-family: 'Tahoma' !important;
        font-size: 32px !important; /* Увеличил, чтобы было как на референсе */
        font-weight: 600 !important;
        color: #314357 !important; /* Глубокий сине-серый с картинки */
        text-align: center !important;
        text-transform: uppercase !important;
        margin-top: 70px !important;   /* Обнуляем отступ */
        margin-bottom: 120px !important;
    }

/* --- КАРТОЧКИ --- */
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




# Функция для вывода карточки
def draw_contact(name, role, icon, email):

    subject = "Трекер привычек"

    st.markdown(f"""
        <div class="dev-card">
            <div class="icon-circle">
                <span class="material-icons-custom">{icon}</span>
            </div>
            <div class="dev-name">{name}</div>
            <div class="dev-role">{role}</div>
            <a href="mailto:{email}?subject={subject}" 
               target="_blank" 
               rel="noopener noreferrer"
               class="dev-email"
               style="display: inline-block; cursor: pointer;">
                {email}
            </a>
        </div>
    """, unsafe_allow_html=True)


_, col1, col2, _ = st.columns([1.5, 2, 2, 1.5])
with col1:
    draw_contact("Самохвалов Семен", "Разработчик", "face", "scpsosat837@gmail.com")
with col2:
    draw_contact("Кис Анна", "Разработчик", "face_2", "a-kisanna@yandex.ru")


col3, col4, col5 = st.columns(3)
with col3:
    draw_contact("Еганова Анастасия", "Менеджер команды", "face_4", "eganova.nastyaa@gmail.com")
with col4:
    draw_contact("Рябинина Ирина", "Дизайнер", "face_3", "irina_ryabinina2007@mail.ru")
with col5:
    draw_contact("Григорян Нарек", "Дизайнер", "face_6", "narek02112020@gmail.com")
