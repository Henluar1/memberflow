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
from modules.map_engine import render_mappa 

# --- SETUP INIZIALE ---
st.set_page_config(page_title="MemberFlow - Assafrica", layout="wide", page_icon="🏛️")
inizializza_db()

# Assicuriamoci che le cartelle necessarie esistano
for folder in ["loghi_soci", "exports"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# CSS Custom per un look professionale e pulito
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #ffffff; 
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stButton>button { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏛️ MemberFlow: Assafrica & Community Manager")

# --- NAVIGAZIONE TABS ---
tabs = st.tabs([
    "➕ Nuovo Socio", 
    "📋 Gestione", 
    "📊 Dashboard & Export", 
    "🌍 Mappa Network", 
    "⚙️ Configurazione"
])

# --- TAB 1: NUOVO SOCIO ---
with tabs[0]:
    ui.render_form_inserimento()

# --- TAB 2: GESTIONE ---
with tabs[1]:
    # Qui abbiamo inserito la possibilità di caricare i loghi mancanti
    ui.render_gestione()

# --- TAB 3: DASHBOARD & EXPORT ---
with tabs[2]:
    ui.render_analytics()
    st.divider()
    
    st.subheader("📥 Centro Esportazione Documenti 2026")
    st.caption("Il sistema genera automaticamente documenti pronti per la stampa con layout ottimizzato.")
    
    c1, c2, c3 = st.columns(3)
    df_attuali = leggi_soci()
    
    with c1:
        st.info("📑 **Catalogo Soci**\n\nLayout 2026: 2 schede fisse per pagina.")
        if st.button("🚀 GENERA CATALOGO PDF", use_container_width=True):
            if not df_attuali.empty:
                with st.spinner("Strutturazione schede in corso..."):
                    # Assicurati che pdf_engine.py sia quello con y_offset fisso (20 e 150)
                    file_path = genera_catalogo(df_attuali) 
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="⬇️ SCARICA CATALOGO PDF",
                                data=f,
                                file_name="Catalogo_Associati_Assafrica_2026.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                type="primary"
                            )
            else:
                st.error("Nessun socio in database.")
            
    with c2:
        st.info("📊 **Report Dati**\n\nAnalisi statistica dei settori e attività.")
        if st.button("📑 GENERA REPORT PDF", use_container_width=True):
            if not df_attuali.empty:
                path_rep = genera_report_dati(df_attuali)
                with open(path_rep, "rb") as f:
                    st.download_button("⬇️ Scarica Report", f, file_name="Analisi_Network_2026.pdf", use_container_width=True)
            
    with c3:
        st.info("📂 **Database Excel**\n\nExport completo per gestione interna.")
        if st.button("📊 ESPORTA LISTA CSV", use_container_width=True):
            if not df_attuali.empty:
                csv = df_attuali.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Scarica CSV", csv, "anagrafica_soci.csv", "text/csv", use_container_width=True)

# --- TAB 4: MAPPA NETWORK ---
with tabs[3]:
    df_mappa = leggi_soci()
    if not df_mappa.empty:
        # Versione con mappa statica a sinistra e card compatte a destra
        render_mappa(df_mappa)
    else:
        st.info("Aggiungi dei soci per visualizzare la distribuzione geografica.")

# --- TAB 5: CONFIGURAZIONE ---
with tabs[4]:
    st.subheader("⚙️ Impostazioni Profilo Associazione")
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