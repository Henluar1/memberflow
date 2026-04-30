import sqlite3
import pandas as pd
import os

DB_PATH = "database_soci.db"

def inizializza_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 1. Creazione Tabella Soci Base
        conn.execute('''CREATE TABLE IF NOT EXISTS soci 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      nome TEXT, categoria TEXT, referente TEXT, 
                      email TEXT, sito TEXT, descrizione TEXT, 
                      descrizione_lunga TEXT, logo_path TEXT, 
                      immagine_copertina_path TEXT, pagato TEXT, 
                      sede TEXT, volume_affari TEXT)''')
        
        # Migrazione Sicura: Aggiunta Colonne Extra
        cursor.execute("PRAGMA table_info(soci)")
        colonne_soci = [info[1] for info in cursor.fetchall()]
        
        migrazioni_soci = {
            "descrizione_lunga": "TEXT",
            "immagine_copertina_path": "TEXT",
            "volume_affari": "TEXT" 
        }
        
        for col, dtype in migrazioni_soci.items():
            if col not in colonne_soci:
                conn.execute(f"ALTER TABLE soci ADD COLUMN {col} {dtype}")

        # 2. Creazione Tabella Configurazione Base
        conn.execute('''CREATE TABLE IF NOT EXISTS configurazione 
                     (id INTEGER PRIMARY KEY, 
                      nome_associazione TEXT, 
                      logo_istituzionale TEXT, 
                      indirizzo TEXT, 
                      email_contatto TEXT)''')
        
        # Migrazione Sicura: Aggiunta Social
        cursor.execute("PRAGMA table_info(configurazione)")
        colonne_config = [info[1] for info in cursor.fetchall()]
        
        nuove_colonne_config = [
            "logo_negativo", "sito_web", "linkedin", 
            "facebook", "instagram", "youtube"
        ]
        
        for col in nuove_colonne_config:
            if col not in colonne_config:
                conn.execute(f"ALTER TABLE configurazione ADD COLUMN {col} TEXT")
        
        conn.execute("INSERT OR IGNORE INTO configurazione (id, nome_associazione, sito_web) VALUES (1, 'Assafrica', 'www.assafrica.it')")
        conn.commit()

def salva_config(nome, logo_std, logo_neg, indirizzo, email, sito_web, linkedin, facebook, instagram, youtube):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""UPDATE configurazione SET 
                     nome_associazione=?, logo_istituzionale=?, logo_negativo=?, indirizzo=?, email_contatto=?,
                     sito_web=?, linkedin=?, facebook=?, instagram=?, youtube=?
                     WHERE id=1""", 
                     (nome, logo_std, logo_neg, indirizzo, email, sito_web, linkedin, facebook, instagram, youtube))
        conn.commit()

def leggi_config():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        res = conn.execute("SELECT * FROM configurazione WHERE id=1").fetchone()
        return dict(res) if res else {}

def leggi_soci():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM soci", conn)

def aggiungi_socio(nome, cat, ref, mail, web, desc, desc_lunga, logo, immagine_copertina, pagato, sede, volume_affari):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""INSERT INTO soci (nome, categoria, referente, email, sito, descrizione, descrizione_lunga, logo_path, immagine_copertina_path, pagato, sede, volume_affari) 
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", 
                     (nome, cat, ref, mail, web, desc, desc_lunga, logo, immagine_copertina, pagato, sede, volume_affari))
        conn.commit()

def aggiorna_socio(id_socio, nome, cat, ref, mail, web, desc, desc_lunga, logo, immagine_copertina, pagato, sede, volume_affari):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""UPDATE soci SET 
                     nome=?, categoria=?, referente=?, email=?, sito=?, descrizione=?, descrizione_lunga=?, logo_path=?, immagine_copertina_path=?, pagato=?, sede=?, volume_affari=? 
                     WHERE id=?""", 
                     (nome, cat, ref, mail, web, desc, desc_lunga, logo, immagine_copertina, pagato, sede, volume_affari, id_socio))
        conn.commit()

def elimina_socio(id_socio):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM soci WHERE id = ?", (id_socio,))
        conn.commit()