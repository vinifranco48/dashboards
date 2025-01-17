from config.db_config import get_database
import logging
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

def validate_user(email: str, senha: str) -> tuple[bool, str]:
    """
    Valida o usuário com base no email e senha fornecidos.
    Retorna uma tupla (success, message).
    """
    try:
        conn = get_database()
        if not conn:
            return False, "Erro ao conectar ao banco de dados."
        
        with conn.cursor() as cursor:  # Usar DictCursor aqui
            query = "SELECT email, senha FROM usuarios WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            if user:
                # Verifica se a senha fornecida corresponde à senha criptografada no banco
                if check_password_hash(user['senha'], senha):
                    return True, "Login bem-sucedido!"
                else:
                    return False, "Email ou senha incorretos."
            else:
                return False, "Email ou senha incorretos."
    
    except Exception as e:
        logger.error(f"Erro ao validar usuário: {str(e)}")
        return False, f"Erro ao validar usuário: {str(e)}"
    
    finally:
        if conn:
            conn.close()

def create_user(email: str, senha: str) -> bool:
    """
    Cria um novo usuário com email e senha criptografada.
    Retorna True se o usuário foi criado com sucesso, False caso contrário.
    """
    conn = get_database()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            # Criptografa a senha antes de armazená-la no banco
            hashed_password = generate_password_hash(senha)
            query = "INSERT INTO usuarios (email, senha) VALUES (%s, %s)"
            cursor.execute(query, (email, hashed_password))
            conn.commit()
            return True
    
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {str(e)}")
        return False
    
    finally:
        if conn:
            conn.close()