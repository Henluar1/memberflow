import streamlit as st
from motore import styles
import motore.ui_components as ui

# --- SETUP PAGINA ---
st.set_page_config(page_title="Gestione Anagrafiche", page_icon="📋", layout="wide")
styles.apply_styles()

# --- RENDER DELLA GESTIONE ---
# Chiama la funzione che abbiamo costruito in ui_components.py
ui.render_gestione()
ui.render_sidebar_footer()