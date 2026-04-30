import streamlit as st
from motore import styles
import motore.ui_components as ui

st.set_page_config(page_title="Export Documenti", layout="wide", page_icon="📥")
styles.apply_styles()

ui.render_export_documenti()
ui.render_sidebar_footer()