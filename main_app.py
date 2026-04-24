import streamlit as st
import os
from PIL import Image

# Importiamo le funzioni dai moduli
from modules.database_manager import (
    inizializza_db, leggi_soci, aggiungi_socio, 
    leggi_config, salva_config
)
from modules.pdf_engine import genera_catalogo
from modules.report_generator import genera_report_dati
import modules.ui_components as ui
from modules.map_engine import render_mappa  # <--- Nuova integrazione

# --- SETUP INIZIALE ---
st.set_page_config(page_title="MemberFlow - Assafrica", layout="wide", page_icon="🏛️")
inizializza_db()

# Assicuriamoci che la cartella loghi esista
if not os.path.exists("loghi_soci"):
    os.makedirs("loghi_soci")

st.title("🏛️ MemberFlow: Assafrica & Community Manager")

# --- NAVIGAZIONE TABS (Ora sono 6) ---
tabs = st.tabs([
    "➕ Nuovo Socio", 
    "📋 Gestione", 
    "📊 Analytics", 
    "🌍 Mappa Network", # <--- Nuova Tab
    "⚙️ Configurazione", 
    "📑 Export"
])

# --- TAB 1: NUOVO SOCIO ---
with tabs[0]:
    ui.render_form_inserimento()

# --- TAB 2: GESTIONE ---
with tabs[1]:
    ui.render_gestione()

# --- TAB 3: ANALYTICS ---
with tabs[2]:
    ui.render_analytics()
    st.divider()
    
    st.subheader("📥 Esportazione Dati Strategici")
    c1, c2 = st.columns(2)
    
    df_attuali = leggi_soci()
    
    with c1:
        if st.button("📑 Genera Report PDF Analytics"):
            if not df_attuali.empty:
                path_rep = genera_report_dati(df_attuali)
                with open(path_rep, "rb") as f:
                    st.download_button("⬇️ Scarica Report PDF", f, file_name="Report_Analisi_2026.pdf")
            else:
                st.warning("Nessun dato da analizzare.")
            
    with c2:
        if st.button("📊 Excel: Esporta Lista Completa"):
            if not df_attuali.empty:
                csv = df_attuali.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Scarica CSV per Excel", csv, "lista_soci.csv", "text/csv")

# --- TAB 4: MAPPA NETWORK ---
with tabs[3]:
    df_mappa = leggi_soci()
    if not df_mappa.empty:
        render_mappa(df_mappa)
    else:
        st.info("Aggiungi dei soci nel database per visualizzare la distribuzione geografica sulla mappa.")

# --- TAB 5: CONFIGURAZIONE ---
with tabs[4]:
    st.subheader("⚙️ Profilo Associazione")
    conf = leggi_config()
    
    with st.form("config_form"):
        col1, col2 = st.columns(2)
        nome_ass = col1.text_input("Nome Associazione", value=conf.get('nome_associazione', 'Assafrica'))
        email_ass = col1.text_input("Email Istituzionale", value=conf.get('email_contatto', ''))
        indirizzo_ass = col2.text_input("Indirizzo Sede", value=conf.get('indirizzo', ''))
        logo_inst = st.file_uploader("Upload Logo Istituzionale (per Intestazioni)", type=["png", "jpg"])
        
        if st.form_submit_button("Aggiorna Impostazioni"):
            logo_path = conf.get('logo_istituzionale', '')
            if logo_inst:
                logo_path = f"loghi_soci/LOGO_ISTITUZIONALE.png"
                Image.open(logo_inst).save(logo_path)
            
            salva_config(nome_ass, logo_path, indirizzo_ass, email_ass)
            st.success("Configurazione salvata con successo!")
            st.rerun()

# --- TAB 6: EXPORT ---
with tabs[5]:
    st.subheader("📑 Esportazione Catalogo")
    if st.button("🚀 GENERA CATALOGO COMPLETO"):
        df_exp = leggi_soci()
        if not df_exp.empty:
            file_path = genera_catalogo(df_exp)
            with open(file_path, "rb") as f:
                st.download_button("⬇️ Scarica Catalogo PDF", f, file_name="Catalogo_Associati_2026.pdf")
        else:
            st.error("Il database è vuoto. Impossibile generare il catalogo.")