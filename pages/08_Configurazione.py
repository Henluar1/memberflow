import streamlit as st
import os
from modules import styles
from modules.database_manager import leggi_config, salva_config

st.set_page_config(page_title="Configurazione", layout="wide", page_icon="⚙️")
styles.apply_styles()

st.markdown("#### ⚙️ Impostazioni Profilo")
conf = leggi_config()

with st.form("config_form"):
    col1, col2 = st.columns(2)
    nome_ass = col1.text_input("Nome Associazione", value=conf.get('nome_associazione', 'Assafrica'))
    email_ass = col1.text_input("Email Contatto", value=conf.get('email_contatto', ''))
    indirizzo_ass = col2.text_input("Sede Legale", value=conf.get('indirizzo', ''))
    
    st.write("---")
    st.markdown("**🖼️ Gestione Loghi Istituzionali**")
    c_l1, c_l2 = st.columns(2)
    logo_inst = c_l1.file_uploader("Logo per sfondo CHIARO (Standard)", type=["png", "jpg", "jpeg"])
    logo_neg = c_l2.file_uploader("Logo per sfondo SCURO (Bianco/Negative)", type=["png", "jpg", "jpeg"])
    
    if st.form_submit_button("Salva Modifiche"):
        path_std = conf.get('logo_istituzionale', '')
        path_neg = conf.get('logo_negativo', '')
        
        if not os.path.exists("loghi_soci"): os.makedirs("loghi_soci")
        
        if logo_inst:
            ext_std = logo_inst.name.split('.')[-1].lower()
            path_std = f"loghi_soci/LOGO_STD.{ext_std}"
            with open(path_std, "wb") as f:
                f.write(logo_inst.getbuffer())
        
        if logo_neg:
            ext_neg = logo_neg.name.split('.')[-1].lower()
            path_neg = f"loghi_soci/LOGO_NEG.{ext_neg}"
            with open(path_neg, "wb") as f:
                f.write(logo_neg.getbuffer())
        
        salva_config(nome_ass, path_std, path_neg, indirizzo_ass, email_ass)
        st.success("Configurazione salvata correttamente!")
        st.rerun()