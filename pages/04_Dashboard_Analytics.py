import streamlit as st
from motore import styles
import motore.ui_components as ui

# --- SETUP PAGINA ---
st.set_page_config(page_title="Dashboard Analytics", page_icon="📊", layout="wide")
styles.apply_styles()

# --- RENDER ANALYTICS ---
ui.render_analytics()
ui.render_sidebar_footer()