import sqlite3
import pandas as pd
import os

DB_PATH = "database_soci.db"

def inizializza_db():
    with sqlite3.connect(DB_PATH) as conn:
        # Tabella Soci
        conn.execute('''CREATE TABLE IF NOT EXISTS soci 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      nome TEXT, categoria TEXT, referente TEXT, 
                      email TEXT, sito TEXT, descrizione TEXT, 
                      logo_path TEXT, pagato TEXT)''')
        
        # Tabella Configurazione (Singola riga)
        conn.execute('''CREATE TABLE IF NOT EXISTS configurazione 
                     (id INTEGER PRIMARY KEY, nome_associazione TEXT, 
                      logo_istituzionale TEXT, indirizzo TEXT, email_contatto TEXT)''')
        
        # Inseriamo una riga vuota se non esiste
        conn.execute("INSERT OR IGNORE INTO configurazione (id, nome_associazione) VALUES (1, 'Assafrica')")
        conn.commit()

def salva_config(nome, logo, indirizzo, email):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""UPDATE configurazione SET 
                     nome_associazione=?, logo_istituzionale=?, indirizzo=?, email_contatto=? 
                     WHERE id=1""", (nome, logo, indirizzo, email))
        conn.commit()

def leggi_config():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        res = conn.execute("SELECT * FROM configurazione WHERE id=1").fetchone()
        return dict(res) if res else {}

def leggi_soci():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM soci", conn)

def aggiungi_socio(nome, cat, ref, mail, web, desc, logo, pagato):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""INSERT INTO soci (nome, categoria, referente, email, sito, descrizione, logo_path, pagato) 
                     VALUES (?,?,?,?,?,?,?,?)""", (nome, cat, ref, mail, web, desc, logo, pagato))
        conn.commit()

def aggiorna_socio(id_socio, nome, cat, ref, mail, web, desc, logo, pagato):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""UPDATE soci SET 
                     nome=?, categoria=?, referente=?, email=?, sito=?, descrizione=?, logo_path=?, pagato=? 
                     WHERE id=?""", (nome, cat, ref, mail, web, desc, logo, pagato, id_socio))
        conn.commit()

def elimina_socio(id_socio):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM soci WHERE id = ?", (id_socio,))
        conn.commit()