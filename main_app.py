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
from modules.pdf_engine import genera_catalogo, genera_scheda_socio 
from modules.report_generator import genera_report_dati
import modules.ui_components as ui
from modules.map_engine import render_mappa 

# --- SETUP INIZIALE ---
st.set_page_config(
    page_title="MemberFlow - Assafrica", 
    layout="wide", 
    page_icon="🏛️",
    initial_sidebar_state="collapsed" 
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

# --- NAVIGAZIONE TABS ---
tabs = st.tabs([
    "➕ Nuovo Socio", 
    "📋 Gestione", 
    "💸 Amministrazione", 
    "📊 Dashboard", 
    "📥 Export",          
    "🌍 Mappa Network", 
    "⚙️ Config"
])

# --- TAB 1: NUOVO SOCIO ---
with tabs[0]:
    ui.render_form_inserimento()

# --- TAB 2: GESTIONE ---
with tabs[1]:
    ui.render_gestione()

# --- TAB 3: AMMINISTRAZIONE (Solleciti) ---
with tabs[2]:
    ui.render_amministrazione()

# --- TAB 4: DASHBOARD ---
with tabs[3]:
    ui.render_analytics()

# --- TAB 5: EXPORT DOCUMENTI (Unificato) ---
with tabs[4]:
    st.markdown("#### 📥 Centro Esportazione Documenti 2026")
    st.markdown("Genera documenti globali o schede individuali basate sui dati attuali.")
    st.write("") 
    
    # Sezione 1: Export Globali
    c1, c2, c3 = st.columns(3)
    df_attuali = leggi_soci()
    
    with c1:
        if st.button("🚀 CATALOGO PDF", use_container_width=True):
            if not df_attuali.empty:
                with st.spinner("Generazione..."):
                    file_path = genera_catalogo(df_attuali) 
                    with open(file_path, "rb") as f:
                        st.download_button("⬇️ SCARICA CATALOGO", f, "Catalogo_Assafrica_2026.pdf", "application/pdf", use_container_width=True)
            else: st.error("Database vuoto.")
            
    with c2:
        if st.button("📑 REPORT ANALITICO", use_container_width=True):
            if not df_attuali.empty:
                with st.spinner("Analisi..."):
                    path_rep = genera_report_dati(df_attuali)
                    with open(path_rep, "rb") as f:
                        st.download_button("⬇️ SCARICA REPORT", f, "Report_Analisi_2026.pdf", "application/pdf", use_container_width=True)
            else: st.error("Database vuoto.")
            
    with c3:
        if st.button("📊 LISTA EXCEL (CSV)", use_container_width=True):
            if not df_attuali.empty:
                csv = df_attuali.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ SCARICA CSV", csv, "export_soci.csv", "text/csv", use_container_width=True)
            else: st.error("Database vuoto.")

    # Sezione 2: One-Pager Individuale
    st.write("")
    st.markdown("---")
    st.markdown("##### 📄 Esporta Scheda Singola Socio (One-Pager)")
    st.info("Genera un documento di presentazione istituzionale per un singolo associato.")
    
    if not df_attuali.empty:
        nomi_soci = sorted(df_attuali['nome'].tolist())
        col_sel, col_btn = st.columns([3, 1])
        socio_nome = col_sel.selectbox("Seleziona l'Associato", nomi_soci, label_visibility="collapsed")
        
        if col_btn.button("✨ GENERA ONE-PAGER", use_container_width=True):
            socio_data = df_attuali[df_attuali['nome'] == socio_nome].iloc[0]
            with st.spinner(f"Creazione scheda per {socio_nome}..."):
                path_scheda = genera_scheda_socio(socio_data)
                if os.path.exists(path_scheda):
                    with open(path_scheda, "rb") as f:
                        st.download_button(
                            label=f"⬇️ SCARICA SCHEDA {socio_nome.upper()}",
                            data=f,
                            file_name=os.path.basename(path_scheda),
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )
    else:
        st.warning("Aggiungi dei soci per abilitare l'export delle schede.")

# --- TAB 6: MAPPA NETWORK ---
with tabs[5]:
    df_mappa = leggi_soci()
    if not df_mappa.empty:
        render_mappa(df_mappa)
    else:
        st.info("Nessun dato per la mappa.")

# --- TAB 7: CONFIGURAZIONE (Aggiornato con Logo Chiaro/Scuro) ---
with tabs[6]:
    st.markdown("#### ⚙️ Impostazioni Profilo")
    conf = leggi_config()
    
    with st.form("config_form"):
        col1, col2 = st.columns(2)
        nome_ass = col1.text_input("Nome Associazione", value=conf.get('nome_associazione', 'Assafrica'))
        email_ass = col1.text_input("Email Contatto", value=conf.get('email_contatto', ''))
        indirizzo_ass = col2.text_input("Sede Legale", value=conf.get('indirizzo', ''))
        
        st.write("---")
        st.markdown("**🖼️ Gestione Loghi Istituzionali**")
        c_l1, c_l2 = st.columns(2)
        logo_inst = c_l1.file_uploader("Logo per sfondo CHIARO (Standard)", type=["png", "jpg", "jpeg"])
        logo_neg = c_l2.file_uploader("Logo per sfondo SCURO (Bianco/Negative)", type=["png", "jpg", "jpeg"])
        
        if st.form_submit_button("Salva Modifiche"):
            path_std = conf.get('logo_istituzionale', '')
            path_neg = conf.get('logo_negativo', '')
            
            if not os.path.exists("loghi_soci"): os.makedirs("loghi_soci")
            
            if logo_inst:
                ext_std = logo_inst.name.split('.')[-1].lower()
                path_std = f"loghi_soci/LOGO_STD.{ext_std}"
                with open(path_std, "wb") as f:
                    f.write(logo_inst.getbuffer())
            
            if logo_neg:
                ext_neg = logo_neg.name.split('.')[-1].lower()
                path_neg = f"loghi_soci/LOGO_NEG.{ext_neg}"
                with open(path_neg, "wb") as f:
                    f.write(logo_neg.getbuffer())
            
            salva_config(nome_ass, path_std, path_neg, indirizzo_ass, email_ass)
            st.success("Configurazione salvata correttamente!")
            st.rerun()