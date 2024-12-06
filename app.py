import streamlit as st
from utils.gsheet import connect_to_gsheet, load_sheet_data
from utils.auth import validate_user, validate_user_data
import os

# Dinamicamente importar componentes
from importlib import import_module

# Configurações de página
st.set_page_config(
    page_title="Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações globais
def load_credentials():
    return {
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

def custom_sidebar_style():
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                background-color: white;
                padding: 20px;
                border-right: 1px solid #e5e5e5;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

# Carregar componentes dinamicamente
def load_components():
    components = {}
    for filename in os.listdir("components"):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            module = import_module(f"components.{module_name}")
            components[module_name.capitalize()] = getattr(module, module_name)
    return components

PAGES = load_components()

# Login
def login_page(users_df):
    st.title("Login")
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("Email", placeholder="Digite seu email")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        submit = st.form_submit_button("Entrar")
        if submit:
            if not email or not senha:
                st.warning("Por favor, preencha todos os campos.")
            elif validate_user(email, senha, users_df):
                st.session_state['logado'] = True
                st.session_state['usuario'] = email
                st.session_state['selected_page'] = "Dashboard"
                st.rerun()
            else:
                st.error("Email ou senha incorretos")

# Barra Lateral
def render_sidebar():
    st.sidebar.title("Navegação")
    if 'usuario' in st.session_state:
        st.sidebar.markdown(f"**Usuário:** {st.session_state['usuario']}")

    for page_name in PAGES.keys():
        if st.sidebar.button(page_name):
            st.session_state['selected_page'] = page_name

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

# Entrada principal
def main():
    custom_sidebar_style()

    if 'logado' not in st.session_state:
        st.session_state['logado'] = False

    if not st.session_state['logado']:
        credentials = load_credentials()
        sheet = connect_to_gsheet("credenciais", credentials)
        users_df = load_sheet_data(sheet)
        validate_user_data(users_df)
        login_page(users_df)
    else:
        render_sidebar()
        selected_page = st.session_state.get("selected_page", "Dashboard")
        if selected_page in PAGES:
            PAGES[selected_page]()
        else:
            st.title("Bem-vindo ao Dashboard!")

if __name__ == "__main__":
    main()
