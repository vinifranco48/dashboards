import streamlit as st



def pagina_inicial(custom_sidebar_style,connect_to_gsheet,carregar_usuarios,login_page,render_sidebar):
    """
    Main application entry point.
    """
    # Apply custom sidebar styling
    custom_sidebar_style()

    # Initialize session state
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False

    # Connect to Google Sheets and load users
    SHEET_NAME = "credenciais"
    sheet = connect_to_gsheet(SHEET_NAME)
    usuarios_df = carregar_usuarios(sheet)

    # Render login or dashboard based on authentication status
    if not st.session_state['logado']:
        login_page(usuarios_df)
    else:
        render_sidebar()
        st.title("Bem-vindo ao Dashboard")