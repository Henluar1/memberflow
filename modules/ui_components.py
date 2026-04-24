import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import Image
from modules.database_manager import leggi_soci, aggiorna_socio, elimina_socio, aggiungi_socio

# Lista ufficiale dei 54 paesi africani
PAESI_AFRICA = [
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Camerun", "Capo Verde", 
    "Ciad", "Comore", "Costa d'Avorio", "Egitto", "Eritrea", "Eswatini", "Etiopia", "Gabon", 
    "Gambia", "Ghana", "Gibuti", "Guinea", "Guinea Equatoriale", "Guinea-Bissau", "Kenya", 
    "Lesotho", "Liberia", "Libia", "Madagascar", "Malawi", "Mali", "Marocco", "Mauritania", 
    "Mauritius", "Mozambico", "Namibia", "Niger", "Nigeria", "Repubblica Centrafricana", 
    "Repubblica del Congo", "Repubblica Democratica del Congo", "Ruanda", "Sahara Occidentale", 
    "Sant'Elena", "São Tomé e Príncipe", "Senegal", "Seychelles", "Sierra Leone", "Somalia", 
    "Sudafrica", "Sudan", "Sudan del Sud", "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
]

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
        
        st.write("---")
        st.write("🌍 **Presenza nel Continente**")
        tutto_continente = st.toggle("Opera in tutta l'Africa")
        
        if tutto_continente:
            paesi_selezionati = ["Tutta l'Africa"]
            st.info("L'azienda verrà mostrata come operativa in ogni stato africano.")
        else:
            paesi_selezionati = st.multiselect("Seleziona i Paesi Operativi", PAESI_AFRICA)
        
        desc = st.text_area("Descrizione")
        logo = st.file_uploader("Logo Aziendale", type=["png", "jpg"])
        
        if st.form_submit_button("SALVA NEL DATABASE"):
            if nome and paesi_selezionati:
                path_logo = ""
                if logo:
                    if not os.path.exists("loghi_soci"): os.makedirs("loghi_soci")
                    path_logo = f"loghi_soci/{nome.replace(' ', '_')}.png"
                    Image.open(logo).save(path_logo)
                
                stringa_paesi = ",".join(paesi_selezionati)
                aggiungi_socio(nome, cat, ref, mail, web, desc, path_logo, pagato, stringa_paesi)
                st.success(f"Azienda {nome} registrata correttamente!")
                st.rerun()
            else:
                st.error("Inserisci almeno la Ragione Sociale e un Paese operativo.")

def render_gestione():
    df = leggi_soci()
    if not df.empty:
        st.subheader("📋 Gestione Anagrafiche")
        cerca = st.text_input("🔍 Filtra per Nome Azienda")
        if cerca:
            df = df[df['nome'].str.contains(cerca, case=False)]
        
        for i, row in df.iterrows():
            with st.expander(f"🏢 {row['nome']} ({row['categoria']})"):
                c1, c2 = st.columns(2)
                new_nome = c1.text_input("Ragione Sociale", value=row['nome'], key=f"n_{row['id']}")
                new_cat = c1.selectbox("Categoria", ["ENERGIA", "ICT", "BANCHE", "EDILIZIA", "LOGISTICA", "ALTRO"], 
                                       index=0, key=f"c_{row['id']}")
                
                new_mail = c2.text_input("Email", value=row['email'], key=f"e_{row['id']}")
                new_pag = c2.selectbox("Stato", ["Pagato", "In attesa"], 
                                       index=0 if row['pagato'] == "Pagato" else 1, key=f"p_{row['id']}")
                
                st.write("**Paesi Operativi:**")
                current_paesi = row['sede'].split(",") if row['sede'] else []
                is_all_africa = "Tutta l'Africa" in current_paesi
                
                edit_tutto = st.toggle("Opera in tutta l'Africa", value=is_all_africa, key=f"togg_{row['id']}")
                if edit_tutto:
                    new_paesi_str = "Tutta l'Africa"
                else:
                    clean_paesi = [p for p in current_paesi if p in PAESI_AFRICA]
                    new_paesi_list = st.multiselect("Modifica Paesi", PAESI_AFRICA, default=clean_paesi, key=f"ms_{row['id']}")
                    new_paesi_str = ",".join(new_paesi_list)
                
                new_desc = st.text_area("Descrizione", value=row['descrizione'], key=f"d_{row['id']}")
                
                col_b1, col_b2 = st.columns(2)
                if col_b1.button("💾 Salva Modifiche", key=f"save_{row['id']}"):
                    aggiorna_socio(row['id'], new_nome, new_cat, row['referente'], new_mail, row['sito'], new_desc, row['logo_path'], new_pag, new_paesi_str)
                    st.success("Dati aggiornati!")
                    st.rerun()
                
                if col_b2.button("🗑️ Elimina", key=f"del_{row['id']}"):
                    elimina_socio(row['id'])
                    st.rerun()

def render_analytics():
    df = leggi_soci()
    if not df.empty:
        st.subheader("📊 Business Intelligence & Geo-Analytics")
        
        # --- ELABORAZIONE GEO-DATI ---
        lista_paesi_flat = []
        presenza_pan_africana = 0
        
        for p_str in df['sede'].dropna():
            if p_str == "Tutta l'Africa":
                presenza_pan_africana += 1
                # Se vogliamo conteggiarli tutti nel grafico a barre, decommentare sotto:
                # lista_paesi_flat.extend(PAESI_AFRICA)
            else:
                lista_paesi_flat.extend([p.strip() for p in p_str.split(",") if p.strip()])
        
        # DataFrame per il grafico dei paesi
        df_geo_counts = pd.Series(lista_paesi_flat).value_counts().reset_index()
        df_geo_counts.columns = ['Paese', 'Numero Aziende']

        # --- METRICHE ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Totale Soci", len(df))
        m2.metric("Mercati Presidiati", len(df_geo_counts))
        m3.metric("Soci Pan-Africani", presenza_pan_africana)
        
        pagati = len(df[df['pagato'] == 'Pagato'])
        m4.metric("Stato Incassi", f"{(pagati/len(df)*100):.1f}%")

        st.divider()

        # --- GRAFICI ---
        c1, c2 = st.columns(2)
        
        with c1:
            # Grafico Categorie
            fig1 = px.pie(df, names='categoria', hole=0.4, 
                          title="Distribuzione per Settore",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig1, use_container_width=True)
            
        with c2:
            # Grafico Top Paesi
            if not df_geo_counts.empty:
                fig2 = px.bar(df_geo_counts.head(10), x='Paese', y='Numero Aziende',
                              title="Top 10 Paesi per Operatività",
                              color='Numero Aziende', color_continuous_scale='Viridis')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Nessun dato geografico specifico disponibile.")

        # --- ANALISI INCASSI ---
        st.write("---")
        fig3 = px.bar(df, x='categoria', color='pagato', barmode='group', 
                      title="Analisi Pagamenti per Categoria Business",
                      color_discrete_map={'Pagato': '#2ecc71', 'In attesa': '#e67e22'})
        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("Aggiungi i primi soci per visualizzare le statistiche.")