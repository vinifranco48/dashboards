import streamlit as st
import os
import sys
from importlib import import_module
import logging
from typing import Dict, Any
from enum import Enum

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import validate_user, create_user
from config.db_config import get_database

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração da página deve ser a primeira chamada Streamlit
st.set_page_config(
    page_title="Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

class UserRole(Enum):
    DIRETOR = "diretor"
    GESTOR_COMERCIAL = "gestor_comercial"
    GESTOR_POSVENDA = "gestor_posvenda"
    VENDEDOR = "vendedor"
    ADM_CNHC = "adm_cnhc"

# Definição de acesso aos dashboards por perfil
ROLE_ACCESS = {
    UserRole.DIRETOR.value: [
        "Dashboard",
        "Comercial",
        "Carros",
        "Yamaha",
        "Gsv",
        "Adm"
    ],
    UserRole.GESTOR_COMERCIAL.value: [
        "Dashboard",
        "Comercial",
        "Carros",
        "Yamaha"
    ],
    UserRole.GESTOR_POSVENDA.value: [
        "Dashboard",
        "Gsv",
        "Yamaha"
    ],
    UserRole.VENDEDOR.value: [
        "Dashboard",
        "Carros",
        "Yamaha"
    ],
    UserRole.ADM_CNHC.value: [
        "Dashboard",
        "Adm"
    ]
}

def get_user_role(email: str) -> str:
    """Obtém o papel do usuário do banco de dados."""
    try:
        conn = get_database()
        if conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT r.role_name 
                    FROM usuarios u
                    JOIN user_roles r ON u.role_id = r.id
                    WHERE u.email = %s
                """
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                return result['role_name'] if result else None
    except Exception as e:
        logger.error(f"Erro ao obter papel do usuário: {e}")
        return None
    finally:
        if conn:
            conn.close()

def check_component_access(component_name: str, user_email: str) -> bool:
    """Verifica se o usuário tem acesso a um componente específico."""
    try:
        role = get_user_role(user_email)
        if not role:
            return False
        return component_name in ROLE_ACCESS.get(role, [])
    except Exception as e:
        logger.error(f"Erro ao verificar acesso ao componente: {e}")
        return False

def filter_accessible_components(components: Dict[str, Any], user_email: str) -> Dict[str, Any]:
    """Filtra os componentes baseado no papel do usuário."""
    try:
        role = get_user_role(user_email)
        if not role:
            logger.error(f"Papel não encontrado para usuário: {user_email}")
            return {}

        allowed_components = ROLE_ACCESS.get(role, [])
        return {name: comp for name, comp in components.items() if name in allowed_components}
    except Exception as e:
        logger.error(f"Erro ao filtrar componentes: {e}")
        return {}

def custom_sidebar_style() -> None:
    """Aplica estilo customizado à sidebar."""
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

def load_components() -> Dict[str, Any]:
    """Carrega dinamicamente os componentes da pasta components."""
    components = {}
    try:
        components_path = os.path.join(os.path.dirname(__file__), "components")
        logger.info(f"Procurando componentes em: {components_path}")
        
        if not os.path.exists(components_path):
            logger.error(f"Diretório de componentes não encontrado: {components_path}")
            return components

        for filename in os.listdir(components_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    module_name = filename[:-3]
                    logger.info(f"Tentando carregar componente: {module_name}")
                    module = import_module(f"components.{module_name}")
                    components[module_name.capitalize()] = getattr(module, module_name)
                    logger.info(f"Componente {module_name} carregado com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao carregar componente {module_name}: {e}")
                    continue
    except Exception as e:
        logger.error(f"Erro ao carregar componentes: {e}")
        st.error("Erro ao carregar componentes. Verifique os logs para mais detalhes.")
    
    return components

def login_page() -> None:
    """Renderiza a página de login."""
    try:
        st.title("Login")
        logger.info("Renderizando formulário de login")
        
        with st.form("login_form", clear_on_submit=True):
            logger.info("Dentro do formulário")
            
            email = st.text_input("Email", placeholder="Digite seu email")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            submit = st.form_submit_button("Entrar")
            
            logger.info(f"Formulário renderizado - Submit: {submit}")
            
            if submit:
                if not email or not senha:
                    logger.warning("Tentativa de login com campos vazios")
                    st.warning("Por favor, preencha todos os campos.")
                    return
                
                try:
                    success, message = validate_user(email, senha)
                    
                    if success:
                        role = get_user_role(email)
                        if role:
                            logger.info(f"Login bem sucedido para usuário: {email}")
                            st.session_state.update({
                                'logado': True,
                                'usuario': email,
                                'role': role,
                                'selected_page': "Dashboard"
                            })
                            st.rerun()
                        else:
                            logger.error(f"Papel não encontrado para usuário: {email}")
                            st.error("Erro ao obter perfil do usuário")
                    else:
                        logger.warning(f"Falha no login: {message}")
                        st.error(message)
                        
                except Exception as e:
                    logger.error(f"Erro na validação do usuário: {str(e)}")
                    st.error(f"Erro ao tentar fazer login: {str(e)}")
                    
    except Exception as e:
        logger.error(f"Erro na página de login: {str(e)}")
        st.error("Erro ao carregar página de login. Tente novamente mais tarde.")

def render_sidebar(pages: Dict[str, Any]) -> None:
    """Renderiza a sidebar com navegação baseada em permissões."""
    try:
        st.sidebar.title("Navegação")
        
        if 'usuario' in st.session_state:
            user_email = st.session_state['usuario']
            role = st.session_state.get('role', '')
            st.sidebar.markdown(f"**Usuário:** {user_email}")
            st.sidebar.markdown(f"**Perfil:** {role}")
            
            for page_name in pages.keys():
                if check_component_access(page_name, user_email):
                    if st.sidebar.button(page_name):
                        st.session_state['selected_page'] = page_name
                        st.rerun()
        
        if st.sidebar.button("Sair"):
            st.session_state.clear()
            st.rerun()
            
    except Exception as e:
        logger.error(f"Erro ao renderizar sidebar: {e}")
        st.sidebar.error("Erro ao carregar navegação")

def initialize_session_state() -> None:
    """Inicializa o estado da sessão com valores padrão."""
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
    if 'selected_page' not in st.session_state:
        st.session_state['selected_page'] = "Dashboard"

def main() -> None:
    """Função principal da aplicação com controle de acesso."""
    try:
        logger.info("Iniciando aplicação")
        
        initialize_session_state()
        custom_sidebar_style()
        
        # Carregar todos os componentes disponíveis
        all_components = load_components()
        
        if not st.session_state['logado']:
            logger.info("Usuário não logado, redirecionando para login")
            login_page()
        else:
            # Filtrar componentes baseado no papel do usuário
            accessible_components = filter_accessible_components(
                all_components, 
                st.session_state['usuario']
            )
            
            render_sidebar(accessible_components)
            
            selected_page = st.session_state.get("selected_page")
            if selected_page in accessible_components:
                try:
                    accessible_components[selected_page]()
                except Exception as e:
                    logger.error(f"Erro ao renderizar página {selected_page}: {e}")
                    st.error(f"Erro ao carregar a página {selected_page}")
            elif selected_page not in all_components:
                st.title("Bem-vindo ao Dashboard!")
            else:
                st.error("Você não tem permissão para acessar esta página.")
                
    except Exception as e:
        logger.error(f"Erro principal: {e}")
        st.error("Ocorreu um erro ao iniciar a aplicação. Por favor, tente novamente mais tarde.")

if __name__ == "__main__":

    main()
