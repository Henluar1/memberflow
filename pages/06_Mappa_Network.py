import streamlit as st
from motore import styles
from motore.database_manager import leggi_soci
from motore.map_engine import render_mappa 

# --- SETUP PAGINA ---
st.set_page_config(page_title="Mappa Network", page_icon="🌍", layout="wide")
styles.apply_styles()

st.markdown("<h2 style='color: #0033A0;'>🌍 Mappa Geografica del Network</h2>", unsafe_allow_html=True)
st.markdown("Esplora interattivamente la presenza delle aziende sul continente africano.")
st.divider()

# 1. Peschiamo i dati aggiornati
df_soci = leggi_soci()

# 2. Disegniamo la mappa solo se ci sono dati
try:
    if not df_soci.empty:
        render_mappa(df_soci) # <-- Eccolo qui! Ora passiamo il 'df' corretto
    else:
        st.info("💡 Aggiungi almeno un'azienda nell'anagrafica per visualizzare i pin sulla mappa.")
except Exception as e:
    st.error(f"⚠️ Impossibile caricare la mappa. Errore: {e}")