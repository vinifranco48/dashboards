from enum import Enum
from typing import Dict, List, Any
import streamlit as st
import logging
from config.db_config import get_database


logger = logging.getLogger(__name__)

class UserRole(Enum):
    DIRETOR = "diretor"
    GESTOR_COMERCIAL = "gestor_comercial"
    GESTOR_POSVENDA = "gestor_posvenda"
    VENDEDOR = "vendedor"
    ADM_CNHC = "adm_cnhc"


ROLE_ACESS ={
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

    try:
        conn = get_database()
        if conn:
            with conn.cursor() as cursor:
                query= """
                    SELECT r.role_name
                    FROM usuarios u
                    JOIN user_roles r ON u.role_id = r.id

                    """
            cursor.execulte(query, (email,))
            result = cursor.fetchone()
            return result['role_name'] if result else None
    except Exception as e:
        logger.error(f"Erro ao obter papel do usuário: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def filter_acessible_components(components: Dict[str, Any], user_email:str) -> Dict[str, Any]:
    try:
        role = get_user_role(user_email)
        if not role:
            logger.error(f"Usuário {user_email} não encontrado no banco de dados")
            return {}
        
        allowed_compenents = ROLE_ACESS.get(role, [])
        return {name: comp for name, comp in components.items() if name in allowed_compenents}
    except Exception as e:
        logger.error(f"Erro ao filtrar componentes acessíveis: {str(e)}")
        return {}

def check_component_acess(component_name:str, user_email:str) -> bool:

    try:
        role = get_user_role(user_email)
        if not role:
            return False
        return component_name in ROLE_ACESS.get(role, [])
    except Exception as e:
        logger.error(f"Erro ao verificar acesso ao componente")
        return False