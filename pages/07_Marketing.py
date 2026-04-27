import streamlit as st
import os
from PIL import Image
from modules import styles
from modules.database_manager import leggi_config

st.set_page_config(page_title="Marketing", layout="wide", page_icon="🎨")
styles.apply_styles()

st.markdown("#### 🎨 Generatore Grafiche Istituzionali")
st.info("Crea grafiche a 3 fasce (Header bianco, Body blu, Footer bianco) come da standard Confindustria.")

col_form, col_preview = st.columns([1.2, 1])

with col_form:
    with st.form("form_banner"):
        st.markdown("**1. Testi Principali**")
        titolo_evento = st.text_input("Titolo Evento", "ENERGY, INFRASTRUCTURE & INDUSTRIAL SECURITY FORUM")
        sottotitolo = st.text_input("Sottotitolo", "From transit corridor to an integrated platform")
        data_luogo = st.text_input("Data e Luogo", "22 May 2026 | Belgrade")
        
        st.markdown("**2. Immagini e Loghi Aggiuntivi**")
        c_img1, c_img2 = st.columns(2)
        loghi_org_files = c_img1.file_uploader("Organizzatori", type=["png", "jpg"], accept_multiple_files=True)
        loghi_part_files = c_img2.file_uploader("Partner", type=["png", "jpg"], accept_multiple_files=True)
        sfondo_file = st.file_uploader("Grafica di Sfondo (Applicherà sfumatura)", type=["png", "jpg"])
        
        st.markdown("**3. Impostazioni**")
        formato = st.selectbox("Formato Ottimizzato", ["LinkedIn Banner (1200x627)", "Instagram Post Quadrato (1080x1080)"])
        
        submitted_banner = st.form_submit_button("🚀 COMPONI GRAFICA", type="primary", use_container_width=True)
        
        if submitted_banner:
            from modules.marketing_engine import genera_banner
            conf = leggi_config()
            logo_inst = conf.get('logo_istituzionale', '')
            
            # Salvataggio temporaneo loghi
            temp_orgs = []
            if loghi_org_files:
                for i, f in enumerate(loghi_org_files):
                    p = f"exports/temp_org_{i}.{f.name.split('.')[-1]}"
                    with open(p, "wb") as f_out: f_out.write(f.getbuffer())
                    temp_orgs.append(p)
            
            temp_parts = []
            if loghi_part_files:
                for i, f in enumerate(loghi_part_files):
                    p = f"exports/temp_part_{i}.{f.name.split('.')[-1]}"
                    with open(p, "wb") as f_out: f_out.write(f.getbuffer())
                    temp_parts.append(p)
                    
            temp_sfondo = None
            if sfondo_file:
                temp_sfondo = f"exports/temp_sfondo.{sfondo_file.name.split('.')[-1]}"
                with open(temp_sfondo, "wb") as f_out: f_out.write(sfondo_file.getbuffer())
            
            tipo = "linkedin" if "LinkedIn" in formato else "instagram"
            
            with st.spinner("Composizione e calcolo sfumature in corso..."):
                path_img = genera_banner(
                    titolo_evento, sottotitolo, data_luogo, tipo, 
                    logo_inst=logo_inst, loghi_org=temp_orgs, loghi_partner=temp_parts, sfondo_dx=temp_sfondo
                )
                st.session_state['last_banner'] = path_img

with col_preview:
    st.markdown("**👁️ Anteprima Risultato**")
    if 'last_banner' in st.session_state and os.path.exists(st.session_state['last_banner']):
        st.image(st.session_state['last_banner'], use_container_width=True)
        with open(st.session_state['last_banner'], "rb") as file:
            st.download_button("⬇️ SCARICA IMMAGINE (JPG)", data=file, file_name="Locandina_Assafrica.jpg", mime="image/jpeg", use_container_width=True, type="primary")
    else:
        st.markdown("<div style='height: 250px; display: flex; align-items: center; justify-content: center; background-color: #f0f2f6; border-radius: 10px; color: #888;'>Compila i dati a sinistra.</div>", unsafe_allow_html=True)