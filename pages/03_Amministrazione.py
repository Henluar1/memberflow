import streamlit as st
from motore import styles
import motore.ui_components as ui

# --- SETUP PAGINA ---
st.set_page_config(page_title="Amministrazione Quote", page_icon="💸", layout="wide")
styles.apply_styles()

# --- RENDER AMMINISTRAZIONE ---
ui.render_amministrazione()
ui.render_sidebar_footer()