import streamlit as st
import os
from PIL import Image

# Importiamo lo stile
from modules import styles 

# Importiamo le funzioni dai moduli
from modules.database_manager import (
    inizializza_db, leggi_soci, aggiungi_socio, 
    leggi_config, salva_config
)
from modules.pdf_engine import genera_catalogo 
from modules.report_generator import genera_report_dati
import modules.ui_components as ui
from modules.map_engine import render_mappa 

# --- SETUP INIZIALE ---
st.set_page_config(
    page_title="MemberFlow - Assafrica", 
    layout="wide", 
    page_icon="🏛️",
    initial_sidebar_state="collapsed" # Risparmia spazio laterale all'avvio
)

# Applica lo stile istituzionale e l'ottimizzazione spazi
styles.apply_styles()
inizializza_db()

# Assicuriamoci che le cartelle necessarie esistano
for folder in ["loghi_soci", "exports"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Titolo compatto per integrazione web
st.markdown(f"<h3 style='text-align: center; margin-bottom: 20px;'>🏛️ MemberFlow Assafrica</h3>", unsafe_allow_html=True)

# --- NAVIGAZIONE TABS (Ora sono 6) ---
tabs = st.tabs([
    "➕ Nuovo Socio", 
    "📋 Gestione", 
    "📊 Dashboard", 
    "📥 Export",          # <-- NUOVO TAB AGGIUNTO QUI
    "🌍 Mappa Network", 
    "⚙️ Config"
])

# --- TAB 1: NUOVO SOCIO ---
with tabs[0]:
    ui.render_form_inserimento()

# --- TAB 2: GESTIONE ---
with tabs[1]:
    ui.render_gestione()

# --- TAB 3: DASHBOARD ---
with tabs[2]:
    ui.render_analytics()

# --- TAB 4: EXPORT DOCUMENTI (Separato) ---
with tabs[3]:
    st.subheader("📥 Centro Esportazione Documenti 2026")
    st.markdown("Genera e scarica i documenti aggiornati basati sui dati attuali del database.")
    st.write("") # Spazio extra
    
    c1, c2, c3 = st.columns(3)
    df_attuali = leggi_soci()
    
    with c1:
        if st.button("🚀 GENERA CATALOGO PDF", use_container_width=True):
            if not df_attuali.empty:
                with st.spinner("Generazione Catalogo in corso..."):
                    file_path = genera_catalogo(df_attuali) 
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="⬇️ SCARICA CATALOGO",
                                data=f,
                                file_name="Catalogo_Associati_Assafrica_2026.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
            else:
                st.error("Database vuoto.")
            
    with c2:
        if st.button("📑 GENERA REPORT PDF", use_container_width=True):
            if not df_attuali.empty:
                with st.spinner("Generazione Report in corso..."):
                    path_rep = genera_report_dati(df_attuali)
                    with open(path_rep, "rb") as f:
                        st.download_button(
                            label="⬇️ SCARICA REPORT", 
                            data=f, 
                            file_name="Analisi_Network_2026.pdf", 
                            use_container_width=True
                        )
            else:
                st.error("Database vuoto.")
            
    with c3:
        if st.button("📊 ESPORTA LISTA CSV", use_container_width=True):
            if not df_attuali.empty:
                csv = df_attuali.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ SCARICA CSV", 
                    data=csv, 
                    file_name="anagrafica_soci.csv", 
                    mime="text/csv", 
                    use_container_width=True
                )
            else:
                st.error("Database vuoto.")

# --- TAB 5: MAPPA NETWORK ---
with tabs[4]:
    df_mappa = leggi_soci()
    if not df_mappa.empty:
        render_mappa(df_mappa)
    else:
        st.info("Aggiungi dei soci per visualizzare la mappa.")

# --- TAB 6: CONFIGURAZIONE ---
with tabs[5]:
    st.subheader("⚙️ Impostazioni Profilo")
    conf = leggi_config()
    
    with st.form("config_form"):
        col1, col2 = st.columns(2)
        nome_ass = col1.text_input("Nome Associazione", value=conf.get('nome_associazione', 'Assafrica'))
        email_ass = col1.text_input("Email Contatto", value=conf.get('email_contatto', ''))
        indirizzo_ass = col2.text_input("Sede Legale", value=conf.get('indirizzo', ''))
        logo_inst = st.file_uploader("Aggiorna Logo Istituzionale", type=["png", "jpg"])
        
        if st.form_submit_button("Salva Modifiche"):
            logo_path = conf.get('logo_istituzionale', '')
            if logo_inst:
                logo_path = f"loghi_soci/LOGO_ISTITUZIONALE.png"
                Image.open(logo_inst).save(logo_path)
            
            salva_config(nome_ass, logo_path, indirizzo_ass, email_ass)
            st.success("Configurazione salvata!")
            st.rerun()