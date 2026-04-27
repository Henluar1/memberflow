import streamlit as st
from modules import styles
import modules.ui_components as ui

st.set_page_config(page_title="Nuovo Socio", layout="wide", page_icon="➕")
styles.apply_styles()

ui.render_form_inserimento()