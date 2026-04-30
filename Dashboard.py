import streamlit as st
import os
from motore import styles
from motore.database_manager import inizializza_db, leggi_config

# --- SETUP INIZIALE ---
st.set_page_config(page_title="MemberFlow - Assafrica", layout="wide", page_icon="🏛️")

styles.apply_styles()
inizializza_db()

# Creazione automatica cartelle di sistema (incluso il nuovo hub risorse)
for folder in ["loghi_soci", "exports", "risorse"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

conf = leggi_config()
nome_ass = conf.get('nome_associazione', 'Assafrica')

if 'welcome' not in st.session_state:
    st.toast(f"Connessione stabilita con il database {nome_ass}", icon="🛰️")
    st.session_state['welcome'] = True

# --- HEADER (Adattivo al tema Scuro/Chiaro) ---
st.title(f"🏛️ {nome_ass}")
st.subheader("Centro Operativo Business Community 2026")
st.divider()

# --- DASHBOARD LAYOUT ---
st.markdown("#### 📌 Navigazione Rapida")
st.write("") 

col1, col2, col3, col4 = st.columns(4)

# Card 1: Gestione
with col1:
    with st.container(border=True):
        st.markdown("### 👥 Gestione")
        st.write("Anagrafica completa, inserimento nuovi soci e amministrazione quote.")
        st.write("") 
        st.page_link("pages/02_Gestione_Anagrafiche.py", label="Apri Anagrafiche", icon="📋")
        st.page_link("pages/01_Nuovo_Socio.py", label="Aggiungi Socio", icon="➕")

# Card 2: Intelligence
with col2:
    with st.container(border=True):
        st.markdown("### 📈 Intelligence")
        st.write("Analisi geografica e settoriale del network tramite strumenti BI.")
        st.write("")
        st.page_link("pages/04_Dashboard_Analytics.py", label="Vedi Analytics", icon="📊")
        st.page_link("pages/06_Mappa_Network.py", label="Apri Mappa", icon="🌍")

# Card 3: Marketing
with col3:
    with st.container(border=True):
        st.markdown("### 🎨 Marketing")
        st.write("Generazione cataloghi PDF e grafiche istituzionali per social media.")
        st.write("")
        st.page_link("pages/05_Export_Documenti.py", label="Genera Cataloghi", icon="📄")
        st.page_link("pages/07_Marketing.py", label="Marketing Studio", icon="🎨")

# Card 4: Risorse (Aggiornato alla posizione 08)
with col4:
    with st.container(border=True):
        st.markdown("### 📚 Risorse")
        st.write("Kit di primo contatto, presentazioni ufficiali e modulistica scaricabile.")
        st.write("")
        st.page_link("pages/08_Risorse.py", label="Apri Libreria", icon="📂")

st.divider()

# --- FOOTER DI STATO ---
st.markdown("#### ⚙️ Stato del Sistema")
m1, m2, m3 = st.columns(3)

m1.metric(label="Stato Database", value="Online 🟢", delta="Sincronizzato")
m2.metric(label="Versione Software", value="v2.7", delta="Enterprise Edition", delta_color="off")
m3.metric(label="Log Attività", value="Nessun Errore", delta="Ultimo check: in tempo reale", delta_color="normal")
import motore.ui_components as ui
ui.render_sidebar_footer()