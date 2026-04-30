import streamlit as st
from motore import styles
import motore.ui_components as ui

# --- SETUP PAGINA ---
st.set_page_config(page_title="Configurazione", layout="wide", page_icon="⚙️")
styles.apply_styles()

# --- RENDER CONFIGURAZIONE ---
ui.render_configurazione()
ui.render_sidebar_footer()