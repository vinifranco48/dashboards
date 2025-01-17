import pymysql
import logging

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_connection.log'),
        logging.StreamHandler()
    ]
)

def test_connection():
    try:
        config = {
            "host": "cpanel.graunahonda.com.br",  # ou o IP do seu servidor
            "user": "grauna",
            "password": "1018337#gm",
            "database": "grauna_bi",
            "port": 3306,
            "connect_timeout": 30  # Aumente o timeout
        }
        
        logging.info("Tentando conectar ao banco de dados...")
        
        # Conecta ao banco de dados usando pymysql
        conn = pymysql.connect(**config)
        
        # Verifica se a conexão foi bem sucedida
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logging.info(f"Conexão bem sucedida! Versão do servidor: {version[0]}")
        
        # Fecha a conexão
        conn.close()
        logging.info("Conexão fechada.")
        
    except pymysql.MySQLError as err:
        logging.error(f"Erro ao conectar ao banco de dados: {err}")
        logging.error(f"Código do erro: {err.args[0]}")
        logging.error(f"Mensagem do erro: {err.args[1]}")
    except Exception as e:
        logging.error(f"Erro inesperado: {e}", exc_info=True)  # Adiciona traceback completo

if __name__ == "__main__":
    test_connection()