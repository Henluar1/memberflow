import streamlit as st
import os
from modules import styles
from modules.database_manager import leggi_soci
from modules.pdf_engine import genera_catalogo, genera_scheda_socio
from modules.report_generator import genera_report_dati

st.set_page_config(page_title="Export Documenti", layout="wide", page_icon="📥")
styles.apply_styles()

st.markdown("#### 📥 Centro Esportazione Documenti 2026")
st.markdown("Genera documenti globali o schede individuali basate sui dati attuali.")
st.write("") 

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