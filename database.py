import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="dinik21.mysql.pythonanywhere-services.com",#"sql7.freesqldatabase.com",
        user="dinik21",#"sql7785733",
        password="Zidane21_mysql",#"lxBTJzfhbh",
        database="dinik21$default",#"sql7785733",
        port=3306
    )

def aggiungi_lavoratore(nome, ruolo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Lavoratori (nome, ruolo) VALUES (%s, %s)", (nome,ruolo))
    conn.commit()
    conn.close()

def aggiungi_cantiere(nome, paese, indirizzo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Cantieri (nome, paese, indirizzo) VALUES (%s, %s, %s)", (nome, paese, indirizzo))
    conn.commit()
    conn.close()

def lista_lavoratori():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, ruolo FROM Lavoratori ORDER BY nome")
    risultati = cursor.fetchall()
    conn.close()
    return risultati

def lista_cantieri():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, paese, indirizzo FROM Cantieri ORDER BY nome")
    risultati = cursor.fetchall()
    conn.close()
    return risultati

def elimina_lavoratore(id_lavoratore):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Lavoratori WHERE id = %s", (id_lavoratore,))
    conn.commit()
    conn.close()

def elimina_cantiere(id_cantiere):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Cantieri WHERE id = %s", (id_cantiere,))
    conn.commit()
    conn.close()

def get_lavoratore(id_lavoratore):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, ruolo FROM Lavoratori WHERE id = %s", (id_lavoratore,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_cantiere(id_cantiere):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, paese, indirizzo FROM Cantieri WHERE id = %s", (id_cantiere,))
    result = cursor.fetchone()
    conn.close()
    return result

def aggiorna_lavoratore(id_lavoratore, nome, ruolo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Lavoratori SET nome = %s, ruolo = %s WHERE id = %s", (nome, ruolo, id_lavoratore))
    conn.commit()
    conn.close()

def aggiorna_cantiere(id_cantiere, nome, paese, indirizzo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Cantieri SET nome = %s, paese = %s, indirizzo = %s WHERE id = %s", (nome, paese, indirizzo, id_cantiere))
    conn.commit()
    conn.close()

def crea_tabella_presenze():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Presenze (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data DATE NOT NULL,
            lavoratore_id INT,
            cantiere_id INT,
            ore DECIMAL(4,2),
            descrizione TEXT,
            FOREIGN KEY (lavoratore_id) REFERENCES Lavoratori(id),
            FOREIGN KEY (cantiere_id) REFERENCES Cantieri(id)
        )
    """)
    conn.commit()
    conn.close()

def aggiungi_presenza(data, lavoratore_id, cantiere_id, ore, descrizione):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Presenze (data, lavoratore_id, cantiere_id, ore, descrizione)
        VALUES (%s, %s, %s, %s, %s)
    """, (data, lavoratore_id, cantiere_id, ore, descrizione))
    conn.commit()
    conn.close()

def aggiungi_presenza(data, lavoratore_id, cantiere_id, ore, descrizione):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Presenze (data, lavoratore_id, cantiere_id, ore, descrizione)
        VALUES (%s, %s, %s, %s, %s)
    """, (data, lavoratore_id, cantiere_id, ore, descrizione))
    conn.commit()
    conn.close()

def report_dettagliato_lavoratore(id_lavoratore, data_inizio, data_fine):
    conn = get_connection()
    cursor = conn.cursor()
    query_totale = """
        SELECT SUM(ore) FROM Presenze
        WHERE lavoratore_id = %s AND data BETWEEN %s AND %s
    """
    cursor.execute(query_totale, (id_lavoratore, data_inizio, data_fine))
    totale = cursor.fetchone()[0] or 0
    query_dettaglio = """
        SELECT c.nome, SUM(p.ore) 
        FROM Presenze p
        JOIN Cantieri c ON p.cantiere_id = c.id
        WHERE p.lavoratore_id = %s AND p.data BETWEEN %s AND %s
        GROUP BY c.nome
    """
    cursor.execute(query_dettaglio, (id_lavoratore, data_inizio, data_fine))
    dettaglio = cursor.fetchall()
    conn.close()
    return totale, dettaglio

def report_dettagliato_cantiere(id_cantiere, data_inizio, data_fine):
    conn = get_connection()
    cursor = conn.cursor()
    query_totale = """
        SELECT SUM(ore) FROM Presenze
        WHERE cantiere_id = %s AND data BETWEEN %s AND %s
    """
    cursor.execute(query_totale, (id_cantiere, data_inizio, data_fine))
    totale = cursor.fetchone()[0] or 0
    query_dettaglio = """
        SELECT l.nome, l.ruolo, SUM(p.ore)
        FROM Presenze p
        JOIN Lavoratori l ON p.lavoratore_id = l.id
        WHERE p.cantiere_id = %s AND p.data BETWEEN %s AND %s
        GROUP BY l.nome, l.ruolo
    """
    cursor.execute(query_dettaglio, (id_cantiere, data_inizio, data_fine))
    dettaglio = cursor.fetchall()
    conn.close()
    return totale, dettaglio

def elimina_presenza(id_presenza):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Presenze WHERE id = %s", (id_presenza,))
    conn.commit()
    conn.close()

def get_presenza(id_presenza):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, data, lavoratore_id, cantiere_id, ore, descrizione FROM Presenze WHERE id = %s", (id_presenza,))
    result = cursor.fetchone()
    conn.close()
    return result

def aggiorna_presenza(id_presenza, data, lavoratore_id, cantiere_id, ore, descrizione):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Presenze
        SET data = %s, lavoratore_id = %s, cantiere_id = %s, ore = %s, descrizione = %s
        WHERE id = %s
    """, (data, lavoratore_id, cantiere_id, ore, descrizione, id_presenza))
    conn.commit()
    conn.close()

def lista_presenze():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.data, l.nome, c.nome, p.ore, p.descrizione
        FROM Presenze p
        JOIN Lavoratori l ON p.lavoratore_id = l.id
        JOIN Cantieri c ON p.cantiere_id = c.id
        ORDER BY p.data DESC
    """)
    risultati = cursor.fetchall()
    conn.close()
    return risultati
