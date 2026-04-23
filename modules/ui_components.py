import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import Image
from modules.database_manager import leggi_soci, aggiorna_socio, elimina_socio, aggiungi_socio

def render_form_inserimento():
    st.subheader("Registra una nuova Azienda")
    with st.form("form_nuovo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Ragione Sociale")
        cat = c1.selectbox("Categoria", ["ENERGIA", "ICT", "BANCHE", "EDILIZIA", "LOGISTICA", "ALTRO"])
        ref = c1.text_input("Referente")
        mail = c2.text_input("Email")
        web = c2.text_input("Sito Web")
        pagato = c2.selectbox("Stato Pagamento", ["Pagato", "In attesa"])
        desc = st.text_area("Descrizione")
        logo = st.file_uploader("Logo", type=["png", "jpg"])
        
        if st.form_submit_button("SALVA NEL DATABASE"):
            if nome:
                path_logo = ""
                if logo:
                    if not os.path.exists("loghi_soci"): os.makedirs("loghi_soci")
                    path_logo = f"loghi_soci/{nome.replace(' ', '_')}.png"
                    Image.open(logo).save(path_logo)
                aggiungi_socio(nome, cat, ref, mail, web, desc, path_logo, pagato)
                st.success(f"Azienda {nome} salvata!")
                st.rerun()

def render_gestione():
    df = leggi_soci()
    if not df.empty:
        st.subheader("📋 Gestione Anagrafiche Complete")
        cerca = st.text_input("🔍 Cerca Azienda")
        if cerca:
            df = df[df['nome'].str.contains(cerca, case=False)]
        
        for i, row in df.iterrows():
            with st.expander(f"🏢 {row['nome']} - Modifica Dati"):
                c1, c2 = st.columns(2)
                # Ora tutti i campi sono modificabili
                new_nome = c1.text_input("Ragione Sociale", value=row['nome'], key=f"n_{row['id']}")
                new_cat = c1.selectbox("Categoria", ["ENERGIA", "ICT", "BANCHE", "EDILIZIA", "LOGISTICA", "ALTRO"], 
                                       index=0, key=f"c_{row['id']}")
                new_ref = c1.text_input("Referente", value=row['referente'], key=f"r_{row['id']}")
                
                new_mail = c2.text_input("Email", value=row['email'], key=f"e_{row['id']}")
                new_web = c2.text_input("Sito Web", value=row['sito'], key=f"s_{row['id']}")
                new_pag = c2.selectbox("Stato", ["Pagato", "In attesa"], 
                                       index=0 if row['pagato'] == "Pagato" else 1, key=f"p_{row['id']}")
                
                new_desc = st.text_area("Descrizione", value=row['descrizione'], key=f"d_{row['id']}")
                
                col_b1, col_b2 = st.columns(2)
                if col_b1.button("💾 Salva Modifiche", key=f"save_{row['id']}"):
                    aggiorna_socio(row['id'], new_nome, new_cat, new_ref, new_mail, new_web, new_desc, row['logo_path'], new_pag)
                    st.success("Dati aggiornati!")
                    st.rerun()
                
                if col_b2.button("🗑️ Elimina", key=f"del_{row['id']}"):
                    elimina_socio(row['id'])
                    st.rerun()

def render_analytics():
    df = leggi_soci()
    if not df.empty:
        st.subheader("📊 Business Intelligence")
        m1, m2, m3 = st.columns(3)
        m1.metric("Totale Soci", len(df))
        m2.metric("Settore Leader", df['categoria'].value_counts().idxmax())
        pagati = len(df[df['pagato'] == 'Pagato'])
        m3.metric("Fatturato Coperto", f"{(pagati/len(df)*100):.1f}%")

        c1, c2 = st.columns(2) # Qui avevamo definito c1 e c2
        with c1:
            fig1 = px.pie(df, names='categoria', hole=0.4, title="Distribuzione Settori")
            st.plotly_chart(fig1, use_container_width=True)
        with c2: # <--- Qui c'era l'errore: ora è correttamente 'c2'
            fig2 = px.bar(df, x='categoria', color='pagato', barmode='group', title="Stato Pagamenti")
            st.plotly_chart(fig2, use_container_width=True)