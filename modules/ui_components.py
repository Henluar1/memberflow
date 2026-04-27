import streamlit as st
import pandas as pd
import plotly.express as px
import os
import urllib.parse
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

# Categorie aggiornate basate sul Catalogo Reale 2025
CATEGORIE_REAL = [
    "ENERGIA & AMBIENTE", "MACCHINARI & IMPIANTI", "ICT & DIGITALE", 
    "EDILIZIA & INFRASTRUTTURE", "AGROALIMENTARE", "LOGISTICA & TRASPORTI", 
    "CHIMICA & GOMMA", "SERVIZI ALLE IMPRESE", "BANCHE", "ALTRO"
]

def render_form_inserimento():
    st.markdown("#### 📝 Registra nuova Azienda dal Catalogo")
    
    tab1, tab2 = st.tabs(["Inserimento Singolo", "Importazione Massiva (Excel)"])
    
    with tab1:
        with st.form("form_nuovo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Ragione Sociale")
            cat = c1.selectbox("Settore Merceologico", CATEGORIE_REAL)
            ref = c1.text_input("Referente A&M")
            mail = c2.text_input("Email")
            web = c2.text_input("Sito Web")
            pagato = c2.selectbox("Stato Socio", ["Pagato", "In attesa"])
            
            st.markdown("<hr style='margin: 0.5em 0;'>", unsafe_allow_html=True)
            
            c3, c4 = st.columns(2)
            
            with c3:
                st.markdown("**🌍 Operatività in Africa**")
                tutto_continente = st.toggle("Opera in tutto il continente (Pan-Africana)")
                paesi_selezionati = ["Tutta l'Africa"] if tutto_continente else st.multiselect(
                    "Seleziona Paesi", PAESI_AFRICA, label_visibility="collapsed"
                )
            
            with c4:
                st.markdown("**🖼️ Logo Aziendale**")
                logo_file = st.file_uploader(
                    "Carica logo", type=["png", "jpg", "jpeg"], label_visibility="collapsed"
                )
            
            st.markdown("<hr style='margin: 0.5em 0;'>", unsafe_allow_html=True)
            desc = st.text_area("Descrizione attività (Breve per il catalogo)", height=100)
            
            if st.form_submit_button("💾 SALVA NEL DATABASE", type="primary", use_container_width=True):
                if nome and paesi_selezionati:
                    path_finale = ""
                    if logo_file:
                        if not os.path.exists("loghi_soci"): 
                            os.makedirs("loghi_soci")
                        nome_sicuro = "".join(x for x in nome if x.isalnum() or x in " ").replace(' ', '_').upper()
                        est = logo_file.name.split('.')[-1].lower()
                        path_finale = f"loghi_soci/{nome_sicuro}.{est}"
                        with open(path_finale, "wb") as f:
                            f.write(logo_file.getbuffer())
                    
                    stringa_paesi = ",".join(paesi_selezionati)
                    aggiungi_socio(nome, cat, ref, mail, web, desc, path_finale, pagato, stringa_paesi)
                    st.success(f"✅ Azienda {nome} aggiunta con successo!")
                    st.rerun()

    with tab2:
        st.info("💡 Carica l'Excel dei soci. I loghi andranno aggiunti manualmente dalla scheda 'Gestione'.")
        file_excel = st.file_uploader("Carica file Excel (.xlsx)", type=["xlsx"])
        if file_excel:
            df_raw = pd.read_excel(file_excel, header=None)
            header_row_index = None
            for i, row in df_raw.iterrows():
                vals = [str(v).lower().strip() for v in row.values]
                if 'nome' in vals or 'ragione sociale' in vals:
                    header_row_index = i
                    break
            
            if header_row_index is not None:
                df_import = pd.read_excel(file_excel, skiprows=header_row_index)
                col_map = {str(c).lower().strip(): c for c in df_import.columns}
                
                def get_smart_val(row_data, alias_list, default=""):
                    for alias in alias_list:
                        if alias in col_map:
                            val = row_data[col_map[alias]]
                            return str(val).strip() if pd.notnull(val) else default
                    return default

                if st.button("🚀 AVVIA IMPORTAZIONE MASSIVA"):
                    progress_bar = st.progress(0)
                    for i, index in enumerate(df_import.index):
                        row = df_import.loc[index]
                        nome_val = get_smart_val(row, ['nome', 'ragione sociale', 'azienda'], "Socio Anonimo")
                        if nome_val == "Socio Anonimo" or str(nome_val) == "nan": continue
                        
                        aggiungi_socio(
                            nome_val, 
                            get_smart_val(row, ['categoria', 'settore', 'area'], "ALTRO"), 
                            get_smart_val(row, ['referente', 'contatto'], ""), 
                            get_smart_val(row, ['email', 'mail'], ""), 
                            get_smart_val(row, ['sito', 'web', 'url'], ""), 
                            get_smart_val(row, ['descrizione', 'attività'], ""), 
                            "", 
                            "Pagato", 
                            get_smart_val(row, ['sede', 'paesi', 'operatività'], "Tutta l'Africa")
                        )
                        progress_bar.progress((i + 1) / len(df_import))
                    st.success("Importazione anagrafiche completata!")
                    st.rerun()

def render_gestione():
    st.markdown("#### 📋 Gestione Massiva Anagrafiche")
    df = leggi_soci()
    
    if not df.empty:
        st.info("💡 Usa la tabella per modifiche rapide ai testi. I Paesi operativi e i Loghi si gestiscono dal pannello avanzato in basso.")
        
        edited_df = st.data_editor(
            df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "logo_path": st.column_config.TextColumn("Path Logo", disabled=True),
                "nome": st.column_config.TextColumn("Ragione Sociale", width="medium"),
                "categoria": st.column_config.SelectboxColumn("Settore", options=CATEGORIE_REAL),
                "pagato": st.column_config.SelectboxColumn("Stato", options=["Pagato", "In attesa"]),
                "sito": st.column_config.LinkColumn("Sito Web"),
                "sede": st.column_config.TextColumn("Operatività (Vedi sotto per modificare)", disabled=True) # <-- Bloccato!
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            height=400
        )

        if st.button("💾 SALVA MODIFICHE TESTUALI (Tabella)", type="primary"):
            for _, row in edited_df.iterrows():
                if pd.notna(row.get('id')):
                    aggiorna_socio(
                        row['id'], row['nome'], row['categoria'], row['referente'], 
                        row['email'], row['sito'], row['descrizione'], 
                        row['logo_path'], row['pagato'], row['sede']
                    )
            st.success("Dati testuali aggiornati!")
            st.rerun()

        st.divider()

        st.markdown("#### ⚙️ Editor Avanzato: Loghi e Paesi Operativi")
        with st.expander("Sviluppa per modificare la copertura geografica o caricare un logo"):
            
            nomi_soci = sorted(df['nome'].tolist())
            azienda_scelta = st.selectbox("Seleziona Azienda da modificare:", nomi_soci)
            socio_target = df[df['nome'] == azienda_scelta].iloc[0]
            
            st.markdown("<hr style='margin: 0.5em 0;'>", unsafe_allow_html=True)
            c_logo, c_paesi = st.columns(2)
            
            # --- ZONA LOGO ---
            with c_logo:
                st.markdown("**🖼️ Gestione Logo**")
                logo_attuale = socio_target.get('logo_path', '')
                if pd.notna(logo_attuale) and str(logo_attuale).strip() != "" and os.path.exists(str(logo_attuale)):
                    st.image(str(logo_attuale), caption="Logo attuale", width=150)
                else:
                    st.warning("Nessun logo presente.")
                
                nuovo_logo = st.file_uploader(f"Carica nuovo logo", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
            
            # --- ZONA PAESI ---
            with c_paesi:
                st.markdown("**🌍 Copertura Geografica**")
                sede_attuale = str(socio_target.get('sede', ''))
                is_pan_africana = (sede_attuale == "Tutta l'Africa")
                
                tutto_continente_edit = st.toggle("Opera in tutto il continente (Pan-Africana)", value=is_pan_africana, key="tgl_edit")
                
                if tutto_continente_edit:
                    nuovi_paesi = ["Tutta l'Africa"]
                else:
                    paesi_preesistenti = []
                    if sede_attuale and not is_pan_africana:
                        paesi_preesistenti = [p.strip() for p in sede_attuale.split(',') if p.strip() in PAESI_AFRICA]
                    
                    nuovi_paesi = st.multiselect(
                        "Modifica Paesi:", 
                        options=PAESI_AFRICA,
                        default=paesi_preesistenti,
                        key="ms_edit"
                    )
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 CONFERMA MODIFICHE AVANZATE", type="primary", use_container_width=True):
                # Processa Logo
                path_finale = logo_attuale
                if nuovo_logo is not None:
                    if not os.path.exists("loghi_soci"): os.makedirs("loghi_soci")
                    nome_sicuro = "".join(x for x in azienda_scelta if x.isalnum() or x in " ").replace(' ', '_').upper()
                    est = nuovo_logo.name.split('.')[-1].lower()
                    path_finale = f"loghi_soci/{nome_sicuro}.{est}"
                    with open(path_finale, "wb") as f:
                        f.write(nuovo_logo.getbuffer())
                
                # Processa Paesi
                stringa_paesi_aggiornata = ",".join(nuovi_paesi)
                
                try:
                    aggiorna_socio(
                        int(socio_target['id']), 
                        str(socio_target['nome']), 
                        str(socio_target['categoria']), 
                        str(socio_target['referente']), 
                        str(socio_target['email']), 
                        str(socio_target['sito']), 
                        str(socio_target['descrizione']), 
                        path_finale, 
                        str(socio_target['pagato']), 
                        stringa_paesi_aggiornata
                    )
                    st.success(f"✅ Dati e Logo di {azienda_scelta} aggiornati correttamente!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore durante l'aggiornamento: {e}")

        st.divider()
        
        with st.expander("🗑️ Zona Pericolo (Eliminazione)"):
            id_del = st.number_input("ID Socio da rimuovere", step=1, value=0)
            if st.button("ELIMINA DEFINITIVAMENTE"):
                elimina_socio(id_del)
                st.rerun()
    else:
        st.info("Database vuoto.")

def render_analytics():
    df = leggi_soci()
    if not df.empty:
        st.markdown("#### 📊 Business Intelligence & Macro-Trend Africa")
        
        lista_paesi_flat = []
        heatmap_data = []
        for _, row in df.iterrows():
            p_str = str(row.get('sede', ''))
            paesi = PAESI_AFRICA if p_str == "Tutta l'Africa" else [p.strip() for p in p_str.split(",") if p.strip()]
            for p in paesi:
                if p in PAESI_AFRICA:
                    lista_paesi_flat.append(p)
                    heatmap_data.append({'Settore': row['categoria'], 'Paese': p})
            if p_str == "Tutta l'Africa":
                lista_paesi_flat.append("Pan-Africana")

        df_geo_counts = pd.Series(lista_paesi_flat).value_counts().reset_index()
        df_geo_counts.columns = ['Paese', 'Numero Aziende']

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Totale Soci", len(df))
        mercati_f = len(df_geo_counts[df_geo_counts['Paese'] != "Pan-Africana"])
        m2.metric("Mercati Presidiati", mercati_f)
        m3.metric("Aziende Pan-Africane", len(df[df['sede'] == "Tutta l'Africa"]))
        pagati = len(df[df['pagato'] == 'Pagato'])
        reg = (pagati/len(df)*100) if len(df) > 0 else 0
        m4.metric("Regolarità Quote", f"{reg:.1f}%")

        st.divider()

        c1, c2 = st.columns([0.6, 0.4])
        with c1:
            st.markdown("#### 🏆 Top 15 Mercati Strategici")
            top_15 = df_geo_counts[df_geo_counts['Paese'] != "Pan-Africana"].head(15)
            fig_bar = px.bar(top_15, x='Numero Aziende', y='Paese', orientation='h',
                             color='Numero Aziende', color_continuous_scale='Blues', text_auto=True)
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.markdown("#### 🏗️ Treemap dei Settori")
            fig_tree = px.treemap(df, path=['categoria', 'nome'], color='categoria', template="plotly_white")
            fig_tree.update_layout(height=400, margin=dict(t=0, l=0, r=0, b=0))
            st.plotly_chart(fig_tree, use_container_width=True)

        st.divider()

        st.markdown("#### 🛰️ Radar di Penetrazione: Settore vs Paesi")
        if heatmap_data:
            df_heat = pd.DataFrame(heatmap_data)
            df_h_counts = df_heat.groupby(['Settore', 'Paese']).size().reset_index(name='Presenze')
            fig_heat = px.density_heatmap(df_h_counts, x="Paese", y="Settore", z="Presenze",
                                          color_continuous_scale="GnBu", text_auto=True)
            st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("#### 💰 Health Check: Stato Pagamenti per Settore")
        fig_pay = px.histogram(df, x="categoria", color="pagato", barmode="group",
                               color_discrete_map={'Pagato': '#2E86C1', 'In attesa': '#E67E22'})
        st.plotly_chart(fig_pay, use_container_width=True)

def render_amministrazione():
    st.markdown("#### 💸 Amministrazione e Solleciti")
    df = leggi_soci()
    
    if not df.empty:
        df_attesa = df[df['pagato'] == 'In attesa']
        
        c1, c2 = st.columns([1, 3])
        c1.metric("Da sollecitare", len(df_attesa))
        
        st.divider()
        
        if not df_attesa.empty:
            st.info("💡 Clicca su 'Invia Sollecito' per aprire il tuo programma di posta con un'email precompilata pronta da inviare.")
            
            col1, col2, col3, col4 = st.columns([3, 2, 2.5, 2])
            col1.markdown("**🏢 Azienda**")
            col2.markdown("**👤 Referente**")
            col3.markdown("**📧 Email**")
            col4.markdown("**⚡ Azione**")
            
            for _, row in df_attesa.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 2.5, 2])
                
                col1.write(row['nome'])
                col2.write(row['referente'] if pd.notna(row['referente']) else "Non specificato")
                col3.write(row['email'] if pd.notna(row['email']) else "N/A")
                
                with col4:
                    if pd.notna(row['email']) and str(row['email']).strip() != "":
                        oggetto = urllib.parse.quote("Confindustria Assafrica & Mediterraneo - Sollecito Quota Associativa 2026")
                        nome_ref = str(row['referente']) if pd.notna(row['referente']) else "Responsabile"
                        
                        corpo = urllib.parse.quote(
                            f"Gentile {nome_ref},\n\n"
                            f"Con la presente le ricordiamo che la quota associativa per l'azienda {row['nome']} "
                            f"risulta attualmente 'In attesa' di saldo.\n\n"
                            f"La preghiamo di provvedere al più presto per garantire la continuità dei servizi "
                            f"e l'inserimento nel Catalogo Ufficiale 2026.\n\n"
                            f"Restiamo a disposizione per qualsiasi chiarimento.\n\n"
                            f"Cordiali saluti,\n"
                            f"Segreteria Assafrica"
                        )
                        
                        mailto_link = f"mailto:{row['email']}?subject={oggetto}&body={corpo}"
                        st.link_button("✉️ INVIA SOLLECITO", mailto_link, use_container_width=True)
                    else:
                        st.button("Manca Email", disabled=True, key=f"dis_{row['id']}", use_container_width=True)
                
                st.markdown("<hr style='margin: 0px; opacity: 0.2;'>", unsafe_allow_html=True)
                
        else:
            st.success("🎉 Grandioso! Tutte le aziende risultano in regola con i pagamenti.")
    else:
        st.info("Database vuoto.")