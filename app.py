import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
import json
import os
from dotenv import load_dotenv
import os

load_dotenv()
# Import components (ensure these exist in your project)
from components.Carros import carros
from components.yamaha import concorr
from components.gsv import gsv
from components.adm import adm
# Page configuration
st.set_page_config(
    page_title="Dashboard", 
    page_icon="🚗", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

def custom_sidebar_style():
    """
    Applies custom CSS styling to the Streamlit sidebar.
    """
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                background-color: white;
                padding: 20px;
                border-right: 1px solid #e5e5e5;
            }
            section[data-testid="stSidebar"] h1, h2, h3, h4 {
                color: #333;
                font-family: Arial, sans-serif;
                margin-bottom: 20px;
            }
            section[data-testid="stSidebar"] a {
                color: #333;
                font-size: 16px;
                text-decoration: none;
                font-family: Arial, sans-serif;
            }
            section[data-testid="stSidebar"] a:hover {
                color: #007bff;
                text-decoration: underline;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def connect_to_gsheet(sheet_name):

        credentials_info = {
            "type": "service_account",
            "project_id": st.secrets["general"]["PROJECT_ID"],
            "private_key_id": st.secrets["general"]["PRIVATE_KEY_ID"],
            "private_key": st.secrets["general"]["PRIVATE_KEY"],
            "client_email": st.secrets["general"]["CLIENT_EMAIL"],
            "client_id": st.secrets["general"]["CLIENT_ID"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": st.secrets["general"]["CLIENT_X509_CERT_URL"],
    }
        
        credentials = Credentials.from_service_account_info(
            credentials_info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets", 
                "https://www.googleapis.com/auth/drive"
            ]
        )
        client = gspread.authorize(credentials)
        return client.open(sheet_name).sheet1

def carregar_usuarios(sheet):
    """
    Loads users from the Google Sheet.
    """
    if sheet is None:
        return pd.DataFrame()
    
    try:
        dados = sheet.get_all_records()
        df = pd.DataFrame(dados)
        required_columns = ['email', 'senha']
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Missing required column: {col}")
                return pd.DataFrame()
        
        df['senha'] = df['senha'].astype(str)
        return df
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return pd.DataFrame()

def validar_usuario(email, senha, df):
    """
    Validates user credentials.
    """
    if df.empty:
        return False
    
    user = df[df['email'].str.lower() == email.lower()]
    return not user.empty and user.iloc[0]['senha'] == senha

def login_page(usuarios_df):
    """
    Renders the login page.
    """
    st.title("Login")
    
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("Email", placeholder="Digite seu email")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        submit_button = st.form_submit_button("Entrar")
        
        if submit_button:
            if not email or not senha:
                st.warning("Por favor, preencha todos os campos.")
                return
            
            if validar_usuario(email, senha, usuarios_df):
                st.session_state['logado'] = True
                st.session_state['usuario'] = email
                st.session_state['selected_page'] = "Dashboard"
                st.rerun()
            else:
                st.error("Email ou senha incorretos")

def render_sidebar():
    """
    Renders the sidebar with navigation options.
    """
    st.sidebar.title("Navegação")
    
    if 'usuario' in st.session_state:
        st.sidebar.markdown(f"**Usuário:** {st.session_state['usuario']}")
    
    # Navigation buttons
    if st.sidebar.button("Carros"):
        st.session_state['selected_page'] = "Carros"
    if st.sidebar.button("Yamaha"):
        st.session_state['selected_page'] = "Yamaha"
    if st.sidebar.button("GSV"):
        st.session_state['selected_page'] = "GSV"
    if st.sidebar.button("ADM"):
        st.session_state['selected_page'] = "ADM"
    
    if st.sidebar.button("Sair"):
        st.session_state['logado'] = False
        st.session_state.pop('usuario', None)
        st.rerun()

def pagina_inicial():
    """
    Main application entry point.
    """
    custom_sidebar_style()

    if 'logado' not in st.session_state:
        st.session_state['logado'] = False

    SHEET_NAME = "credenciais"
    sheet = connect_to_gsheet(SHEET_NAME)
    usuarios_df = carregar_usuarios(sheet)

    if not st.session_state['logado']:
        login_page(usuarios_df)
    else:
        render_sidebar()
        page = st.session_state.get('selected_page', "Dashboard")
        if page == "Carros":
            carros()
        elif page == "Yamaha":
            concorr()
        elif page == "GSV":
            gsv()
        elif page == "ADM":
            adm()
        else:
            st.title("Bem-vindo ao Dashboard")

if __name__ == "__main__":
    pagina_inicial()
