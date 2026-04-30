import streamlit as st
from motore import styles
import motore.ui_components as ui

st.set_page_config(page_title="Marketing Studio", layout="wide", page_icon="🎨")
styles.apply_styles()

ui.render_marketing_studio()
ui.render_sidebar_footer()