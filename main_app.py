import streamlit as st
import os
from modules import styles
from modules.database_manager import inizializza_db, leggi_config

# --- SETUP INIZIALE GLOBALE ---
st.set_page_config(
    page_title="MemberFlow - Assafrica", 
    layout="wide", 
    page_icon="🏛️"
)

styles.apply_styles()
inizializza_db()

# Assicuriamoci che le cartelle necessarie esistano
for folder in ["loghi_soci", "exports"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

conf = leggi_config()
nome_ass = conf.get('nome_associazione', 'Assafrica')

# --- HOMEPAGE ---
st.markdown(f"<h3 style='text-align: center; margin-bottom: 20px;'>🏛️ MemberFlow {nome_ass}</h3>", unsafe_allow_html=True)
st.sidebar.success("Seleziona una sezione dal menu qui sopra.")

st.markdown("""
### Benvenuto nel Centro Operativo Business Community 2026
Questo software gestionale è stato aggiornato con un'architettura **Multi-Page** per garantire massima velocità, stabilità e sicurezza dei dati.

Utilizza la barra laterale a sinistra per navigare tra gli strumenti:
- **Gestione Soci**: Inserimento, anagrafiche e amministrazione quote.
- **Business Intelligence**: Dashboard analitica e Mappa interattiva.
- **Marketing & Export**: Generatore di grafiche istituzionali e PDF (Cataloghi, Report, Schede).
""")