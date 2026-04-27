import streamlit as st
from modules import styles
import modules.ui_components as ui

st.set_page_config(page_title="Amministrazione", layout="wide", page_icon="💸")
styles.apply_styles()

ui.render_amministrazione()