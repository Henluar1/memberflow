import streamlit as st
from modules import styles
from modules.database_manager import leggi_soci
from modules.map_engine import render_mappa

st.set_page_config(page_title="Mappa Network", layout="wide", page_icon="🌍")
styles.apply_styles()

st.markdown("#### 🌍 Mappa della Presenza in Africa")
df_mappa = leggi_soci()
if not df_mappa.empty:
    render_mappa(df_mappa)
else:
    st.info("Nessun dato per la mappa.")