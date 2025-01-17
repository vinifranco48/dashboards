import mysql.connector

try:
    conn = mysql.connector.connect(
        host="cpanel.graunahonda.com.br",
        user="grauna",
        password="1018337#gm",
        database="grauna_bi"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sua_tabela")
    results = cursor.fetchall()
    print(results)
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
        print("Conexão fechada.")