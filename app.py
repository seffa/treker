import streamlit as st
# from utils import local_css
import base64
from datetime import datetime

st.set_page_config(
    page_title="2",
    layout="wide"
)

def get_base64_img(images):
    with open(images, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

#дата и заголовок
current_date = datetime.now().strftime("%d.%m.%Y")
col1, col2 = st.columns([1, 3])
with col1:
    st.container().write(
        f"""
        <div style="
            background-color: #92AEC3;
            padding: 10px;
            border-radius: 40px;
            text-align: center;
            font-size: 20px;
            color: black;
        ">
            {current_date}
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        "<span style='display: flex;justify-content:center;font-family:Tahoma;font-size:30px'>ГЛАВНАЯ</span>",
        unsafe_allow_html=True
    )






with st.sidebar:
    st.markdown("""
        <style>
            [data-testid="stSidebar"][aria-expanded-true] > div:first-child {
                width: 400px; /* Задайте желаемую ширину */
            }
            [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
                /* Дополнительные стили для сжатой панели */
            }
        </style>
        """, unsafe_allow_html=True)

    st.markdown(
        f'''
            <style>
                .sidebar .sidebar-content {{
                    width: 60px;
                }}
            </style>
        ''',
        unsafe_allow_html=True
    )

    st.sidebar.markdown(f"""
                    <div style="border-radius:15px;overflow:hidden;">
                            <img src="data:image/png;base64,{img_menu}" style="width:120px;border-radius:30px;">
                        </a>
                    </div>
                    """,
                        unsafe_allow_html=True)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    st.sidebar.markdown(f"""
                <div style="border-radius:15px;overflow:hidden;">
                        <a href="/app2"
                        style="display: inline-block; overflow:hidden; border-radius:32px;">
                        <img src="data:image/png;base64,{img_home}" "width:50px;display:block;margin:0 auto;">
                </a>
                </div>
                """,
                        unsafe_allow_html=True)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    st.sidebar.markdown(f"""
                    <div style="border-radius:15px;overflow:hidden;">
                        <a href="/profile2"
                            style="display: inline-block; overflow:hidden; border-radius:32px;">
                            <img src="data:image/png;base64,{img_profile}" "width:50px;display:block;margin:0 auto;">
                        </a>
                    </div>
                    """,
                        unsafe_allow_html=True)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
                <div style="border-radius:15px;overflow:hidden;">
                    <a href="/settings2"
                        style="display: inline-block; overflow:hidden; border-radius:32px;">
                        <img src="data:image/png;base64,{img_fix}" "width:50px;display:block;margin:0 auto;">
                    </a>
                </div>
                """,
                unsafe_allow_html=True)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    st.sidebar.markdown(f"""
                    <div style="border-radius:15px;overflow:hidden;">
                        <a href="/contacts"
                            style="display: inline-block; overflow:hidden; border-radius:32px;">
                            <img src="data:image/png;base64,{img_contacts}" "width:50px;display:block;margin:0 auto;">
                        </a>
                    </div>
                    """,
                        unsafe_allow_html=True)



st.set_page_config(page_title="Main", layout='wide')

# local_css("styles/style.css")
