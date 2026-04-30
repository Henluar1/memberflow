import streamlit as st
from motore import styles
import motore.ui_components as ui

# --- SETUP PAGINA ---
st.set_page_config(page_title="Nuovo Socio", layout="wide", page_icon="➕")
styles.apply_styles()

# --- RENDER DEL FORM ---
ui.render_form_inserimento()
ui.render_sidebar_footer()