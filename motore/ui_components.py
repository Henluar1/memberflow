import streamlit as st
import pandas as pd
import plotly.express as px
import os
import urllib.parse
import json
from PIL import Image

# ⚠️ ATTENZIONE: Usiamo 'motore' e non 'modules'
from motore.database_manager import leggi_soci, aggiorna_socio, elimina_socio, aggiungi_socio, leggi_config, salva_config

# --- COSTANTI GLOBALI ---
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

# Nuova costante per il Volume d'Affari basata sull'immagine fornita
OPZIONI_FATTURATO = [
    "Non specificato",
    "startup",
    "fino a 2 milioni di euro",
    "tra 2 e 10 milioni di euro",
    "tra 10 e 50 milioni di euro",
    "oltre 50 milioni di euro"
]

# --- GESTIONE DINAMICA SETTORI ---
FILE_SETTORI = "config_settori.json"
SETTORI_BASE = [
    "ENERGIA & AMBIENTE", "MACCHINARI & IMPIANTI", "ICT & DIGITALE", 
    "EDILIZIA & INFRASTRUTTURE", "AGROALIMENTARE", "LOGISTICA & TRASPORTI", 
    "CHIMICA & GOMMA", "SERVIZI ALLE IMPRESE", "BANCHE", "ALTRO"
]

def ottieni_categorie():
    """Legge i settori dal file JSON. Se non esiste, lo crea con quelli base."""
    if not os.path.exists(FILE_SETTORI):
        with open(FILE_SETTORI, "w") as f:
            json.dump(SETTORI_BASE, f)
        return SETTORI_BASE
    with open(FILE_SETTORI, "r") as f:
        return json.load(f)

def salva_categorie(nuove_categorie):
    """Salva la lista aggiornata nel file JSON."""
    with open(FILE_SETTORI, "w") as f:
        json.dump(nuove_categorie, f)

# ==========================================
# 01. COMPONENTE: NUOVO SOCIO
# ==========================================
def render_form_inserimento():
    st.markdown("<h2 style='color: #0033A0;'>➕ Registra Nuova Azienda</h2>", unsafe_allow_html=True)
    st.markdown("Aggiungi un'azienda al Catalogo tramite inserimento manuale o importazione massiva da Excel.")
    st.divider()
    
    tab1, tab2 = st.tabs(["✍️ Inserimento Singolo", "📁 Importazione Massiva (Excel)"])
    
    with tab1:
        with st.form("form_nuovo", clear_on_submit=True):
            st.markdown("#### 🏢 Dati Generali")
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Ragione Sociale *")
                cat = st.selectbox("Settore Merceologico", ottieni_categorie())
                ref = st.text_input("Referente A&M")
                pagato = st.selectbox("Stato Socio", ["Pagato", "In attesa"])
            with c2:
                mail = st.text_input("Email")
                web = st.text_input("Sito Web")
                vol_affari = st.selectbox("Volume d'affari", OPZIONI_FATTURATO)
            
            st.divider()
            
            st.markdown("#### 🌍 Dettagli Operativi e Immagini")
            c3, c4 = st.columns(2)
            with c3:
                st.markdown("**Operatività in Africa**")
                tutto_continente = st.toggle("Opera in tutto il continente (Pan-Africana)")
                paesi_selezionati = ["Tutta l'Africa"] if tutto_continente else st.multiselect(
                    "Seleziona Paesi", PAESI_AFRICA, label_visibility="collapsed"
                )
            with c4:
                c_logo, c_cover = st.columns(2)
                logo_file = c_logo.file_uploader("🖼️ Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
                cover_file = c_cover.file_uploader("📸 Foto Presentazione", type=["png", "jpg", "jpeg"])
                st.caption("Tip: La foto sarà lo sfondo della locandina.")
            
            st.divider()
            
            st.markdown("#### 📝 Testi Descrittivi")
            c_desc1, c_desc2 = st.columns(2)
            with c_desc1:
                desc = st.text_area("Descrizione Breve (Per il catalogo globale)", height=150)
            with c_desc2:
                desc_lunga = st.text_area("Descrizione Estesa (Per Locandina One-Pager)", height=150)
            
            if st.form_submit_button("💾 SALVA NEL DATABASE", type="primary", use_container_width=True):
                if nome and paesi_selezionati:
                    path_logo_finale = ""
                    path_cover_finale = ""
                    
                    if not os.path.exists("media/loghi_soci"): os.makedirs("media/loghi_soci")
                    if not os.path.exists("media/foto_presentazione"): os.makedirs("media/foto_presentazione")
                    
                    nome_sicuro = "".join(x for x in nome if x.isalnum() or x in " ").replace(' ', '_').upper()

                    if logo_file:
                        est = logo_file.name.split('.')[-1].lower()
                        path_logo_finale = f"media/loghi_soci/{nome_sicuro}_LOGO.{est}"
                        with open(path_logo_finale, "wb") as f:
                            f.write(logo_file.getbuffer())
                    
                    if cover_file:
                        est = cover_file.name.split('.')[-1].lower()
                        path_cover_finale = f"media/foto_presentazione/{nome_sicuro}_COVER.{est}"
                        with open(path_cover_finale, "wb") as f:
                            f.write(cover_file.getbuffer())
                    
                    stringa_paesi = ",".join(paesi_selezionati)
                    aggiungi_socio(nome, cat, ref, mail, web, desc, desc_lunga, path_logo_finale, path_cover_finale, pagato, stringa_paesi, vol_affari)
                    st.toast(f"Azienda {nome} aggiunta con successo!", icon="✅")
                else:
                    st.error("⚠️ La Ragione Sociale e almeno un Paese sono obbligatori.")

    with tab2:
        st.info("💡 **Tip:** Carica un file Excel. L'intelligenza del sistema mapperà automaticamente le colonne. I loghi andranno aggiunti dal pannello Gestione.")
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

                if st.button("🚀 AVVIA IMPORTAZIONE MASSIVA", type="primary"):
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
                            "", "", "", "Pagato", 
                            get_smart_val(row, ['sede', 'paesi', 'operatività'], "Tutta l'Africa"),
                            "Non specificato"
                        )
                        progress_bar.progress((i + 1) / len(df_import))
                    st.toast("Importazione anagrafiche completata!", icon="🎉")

# ==========================================
# 02. COMPONENTE: GESTIONE ANAGRAFICHE
# ==========================================
def render_gestione():
    st.markdown("<h2 style='color: #0033A0;'>📋 Gestione Anagrafiche</h2>", unsafe_allow_html=True)
    df = leggi_soci()
    
    if not df.empty:
        st.info("💡 **Modifica Rapida:** Clicca sulle celle della tabella per modificare i testi base. L'editor avanzato in basso permette di gestire i testi lunghi, i loghi e i paesi.")
        
        edited_df = st.data_editor(
            df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "logo_path": None,
                "immagine_copertina_path": None,
                "descrizione_lunga": None,
                "nome": st.column_config.TextColumn("Ragione Sociale", width="medium"),
                "categoria": st.column_config.SelectboxColumn("Settore", options=ottieni_categorie()),
                "volume_affari": st.column_config.SelectboxColumn("Fatturato", options=OPZIONI_FATTURATO),
                "pagato": st.column_config.SelectboxColumn("Stato", options=["Pagato", "In attesa"]),
                "sito": st.column_config.LinkColumn("Sito Web"),
                "sede": st.column_config.TextColumn("Operatività (Vedi Editor)", disabled=True)
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            height=400
        )

        if st.button("💾 SALVA MODIFICHE TABELLA", type="primary"):
            for _, row in edited_df.iterrows():
                if pd.notna(row.get('id')):
                    dl = str(row['descrizione_lunga']) if 'descrizione_lunga' in row else ''
                    lp = str(row['logo_path']) if 'logo_path' in row else ''
                    ic = str(row['immagine_copertina_path']) if 'immagine_copertina_path' in row else ''
                    va = str(row['volume_affari']) if 'volume_affari' in row else 'Non specificato'
                    
                    aggiorna_socio(
                        row['id'], row['nome'], row['categoria'], row['referente'], 
                        row['email'], row['sito'], row['descrizione'], dl,
                        lp, ic, row['pagato'], row['sede'], va
                    )
            st.toast("Dati testuali sincronizzati con il database!", icon="🔄")

        st.divider()

        st.markdown("#### ⚙️ Editor Avanzato: Testi, Media e Paesi Operativi")
        with st.expander("Apri per modificare la descrizione lunga, le immagini o la copertura geografica"):
            nomi_soci = sorted(df['nome'].tolist())
            azienda_scelta = st.selectbox("Seleziona Azienda da modificare:", nomi_soci)
            socio_target = df[df['nome'] == azienda_scelta].iloc[0]
            
            st.divider()
            
            # --- ZONA MEDIA ---
            st.markdown("**🖼️ Gestione Media**")
            c_logo, c_cover = st.columns(2)
            
            with c_logo:
                st.markdown("**Logo Aziendale**")
                logo_attuale = socio_target.get('logo_path', '')
                if pd.notna(logo_attuale) and str(logo_attuale).strip() != "" and os.path.exists(str(logo_attuale)):
                    st.image(str(logo_attuale), caption="Logo attuale", width=150)
                else:
                    st.warning("Nessun logo presente.")
                nuovo_logo = st.file_uploader(f"Sostituisci logo", type=["png", "jpg", "jpeg"], key="up_logo")
            
            with c_cover:
                st.markdown("**Foto di Presentazione (Sfondo Locandina)**")
                cover_attuale = socio_target.get('immagine_copertina_path', '') if 'immagine_copertina_path' in socio_target else ''
                if pd.notna(cover_attuale) and str(cover_attuale).strip() != "" and os.path.exists(str(cover_attuale)):
                    st.image(str(cover_attuale), caption="Foto presentazione attuale", width=250)
                else:
                    st.warning("Nessuna foto di presentazione presente.")
                nuovo_cover = st.file_uploader(f"Sostituisci foto presentazione", type=["png", "jpg", "jpeg"], key="up_cover")
            
            st.divider()

            # --- Altri Dati ---
            st.markdown("**🌍 Copertura Geografica e Dimensioni**")
            c_geo, c_fatt = st.columns(2)
            with c_geo:
                sede_attuale = str(socio_target.get('sede', ''))
                is_pan_africana = (sede_attuale == "Tutta l'Africa")
                tutto_continente_edit = st.toggle("Opera in tutto il continente (Pan-Africana)", value=is_pan_africana, key="tgl_edit")
                
                if tutto_continente_edit:
                    nuovi_paesi = ["Tutta l'Africa"]
                else:
                    paesi_preesistenti = [p.strip() for p in sede_attuale.split(',') if p.strip() in PAESI_AFRICA] if (sede_attuale and not is_pan_africana) else []
                    nuovi_paesi = st.multiselect("Modifica Paesi:", options=PAESI_AFRICA, default=paesi_preesistenti, key="ms_edit")
            
            with c_fatt:
                va_attuale = str(socio_target.get('volume_affari', 'Non specificato'))
                nuovo_vol_affari = st.selectbox("Modifica Volume d'affari", OPZIONI_FATTURATO, index=OPZIONI_FATTURATO.index(va_attuale) if va_attuale in OPZIONI_FATTURATO else 0)

            st.markdown("<br>**📝 Testi Aziendali**", unsafe_allow_html=True)
            c_testo1, c_testo2 = st.columns(2)
            
            desc_breve_attuale = str(socio_target.get('descrizione', ''))
            desc_lunga_attuale = str(socio_target.get('descrizione_lunga', '')) if 'descrizione_lunga' in socio_target else ''
            
            nuova_desc_breve = c_testo1.text_area("Descrizione Breve", value=desc_breve_attuale, height=130)
            nuova_desc_lunga = c_testo2.text_area("Descrizione Estesa", value=desc_lunga_attuale, height=130)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 CONFERMA MODIFICHE AVANZATE", type="primary", use_container_width=True):
                if not os.path.exists("media/loghi_soci"): os.makedirs("media/loghi_soci")
                if not os.path.exists("media/foto_presentazione"): os.makedirs("media/foto_presentazione")
                nome_sicuro = "".join(x for x in azienda_scelta if x.isalnum() or x in " ").replace(' ', '_').upper()

                path_logo_finale = logo_attuale
                if nuovo_logo is not None:
                    est = nuovo_logo.name.split('.')[-1].lower()
                    path_logo_finale = f"media/loghi_soci/{nome_sicuro}_LOGO.{est}"
                    with open(path_logo_finale, "wb") as f:
                        f.write(nuovo_logo.getbuffer())
                        
                path_cover_finale = cover_attuale
                if nuovo_cover is not None:
                    est = nuovo_cover.name.split('.')[-1].lower()
                    path_cover_finale = f"media/foto_presentazione/{nome_sicuro}_COVER.{est}"
                    with open(path_cover_finale, "wb") as f:
                        f.write(nuovo_cover.getbuffer())
                
                stringa_paesi_aggiornata = ",".join(nuovi_paesi)
                try:
                    aggiorna_socio(
                        int(socio_target['id']), str(socio_target['nome']), str(socio_target['categoria']), 
                        str(socio_target['referente']), str(socio_target['email']), str(socio_target['sito']), 
                        nuova_desc_breve, nuova_desc_lunga, path_logo_finale, path_cover_finale, str(socio_target['pagato']), stringa_paesi_aggiornata, nuovo_vol_affari
                    )
                    st.toast(f"Dati di {azienda_scelta} aggiornati!", icon="✅")
                    st.rerun() 
                except Exception as e:
                    st.error(f"Errore durante l'aggiornamento: {e}")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🗑️ Zona Pericolo (Eliminazione Definitiva)"):
            st.warning("Attenzione: l'eliminazione è irreversibile.")
            id_del = st.number_input("ID Socio da rimuovere", step=1, value=0)
            if st.button("ELIMINA SOCIO"):
                elimina_socio(id_del)
                st.toast(f"Socio {id_del} eliminato.", icon="🗑️")
    else:
        st.info("Il database è attualmente vuoto.")

# ==========================================
# 03. COMPONENTE: ANALYTICS
# ==========================================
def render_analytics():
    st.markdown("<h2 style='color: #0033A0;'>📊 Business Intelligence</h2>", unsafe_allow_html=True)
    df = leggi_soci()
    
    if not df.empty:
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
        m2.metric("Mercati Presidiati", len(df_geo_counts[df_geo_counts['Paese'] != "Pan-Africana"]))
        m3.metric("Aziende Pan-Africane", len(df[df['sede'] == "Tutta l'Africa"]))
        reg = (len(df[df['pagato'] == 'Pagato'])/len(df)*100) if len(df) > 0 else 0
        m4.metric("Regolarità Quote", f"{reg:.1f}%")

        st.divider()

        # --- PRIMA RIGA DI GRAFICI ---
        c1, c2 = st.columns([0.6, 0.4])
        with c1:
            st.markdown("#### 🏆 Top 15 Mercati Strategici")
            top_15 = df_geo_counts[df_geo_counts['Paese'] != "Pan-Africana"].head(15)
            fig_bar = px.bar(top_15, x='Numero Aziende', y='Paese', orientation='h',
                             color='Numero Aziende', color_continuous_scale='Blues', text_auto=True)
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, showlegend=False, template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.markdown("#### 🏗️ Treemap dei Settori")
            fig_tree = px.treemap(df, path=['categoria', 'nome'], color='categoria', template="plotly_white")
            fig_tree.update_layout(height=400, margin=dict(t=0, l=0, r=0, b=0))
            st.plotly_chart(fig_tree, use_container_width=True)

        st.divider()

        # --- SECONDA RIGA DI GRAFICI ---
        c3, c4 = st.columns([0.5, 0.5])
        
        with c3:
            st.markdown("#### 🛰️ Radar di Penetrazione: Settore vs Paesi")
            if heatmap_data:
                df_heat = pd.DataFrame(heatmap_data)
                df_h_counts = df_heat.groupby(['Settore', 'Paese']).size().reset_index(name='Presenze')
                fig_heat = px.density_heatmap(df_h_counts, x="Paese", y="Settore", z="Presenze",
                                              color_continuous_scale="GnBu", text_auto=True)
                fig_heat.update_layout(template="plotly_white", height=400)
                st.plotly_chart(fig_heat, use_container_width=True)
        
        with c4:
            st.markdown("#### 💰 Distribuzione Dimensionale (Fatturato)")
            if 'volume_affari' in df.columns:
                # Conta le aziende per fascia di fatturato, ignorando quelle non specificate per una vista più pulita
                df_fatturato = df[df['volume_affari'] != 'Non specificato']['volume_affari'].value_counts().reset_index()
                df_fatturato.columns = ['Fascia', 'Numero Aziende']
                
                if not df_fatturato.empty:
                    fig_pie = px.pie(df_fatturato, values='Numero Aziende', names='Fascia', hole=0.4, 
                                     color_discrete_sequence=px.colors.sequential.Blues_r)
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie.update_layout(template="plotly_white", height=400, showlegend=False)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Nessun dato sul fatturato disponibile per generare il grafico.")
            else:
                 st.info("Colonna volume_affari non trovata nel database.")
                 
# ==========================================
# 04. COMPONENTE: AMMINISTRAZIONE
# ==========================================
def render_amministrazione():
    st.markdown("<h2 style='color: #0033A0;'>💸 Amministrazione e Solleciti</h2>", unsafe_allow_html=True)
    df = leggi_soci()
    
    if not df.empty:
        df_attesa = df[df['pagato'] == 'In attesa']
        
        c1, c2 = st.columns([1, 3])
        c1.metric("Quote da sollecitare", len(df_attesa))
        
        st.divider()
        
        if not df_attesa.empty:
            st.info("💡 Clicca su 'Invia Sollecito' per aprire il tuo programma di posta con un'email precompilata.")
            
            col1, col2, col3, col4 = st.columns([3, 2, 2.5, 2])
            col1.caption("AZIENDA")
            col2.caption("REFERENTE")
            col3.caption("EMAIL")
            col4.caption("AZIONE")
            
            for _, row in df_attesa.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 2.5, 2])
                
                col1.write(f"**{row['nome']}**")
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
                            f"La preghiamo di provvedere al più presto per garantire la continuità dei servizi.\n\n"
                            f"Restiamo a disposizione per qualsiasi chiarimento.\n\n"
                            f"Cordiali saluti,\n"
                            f"Segreteria Assafrica"
                        )
                        
                        mailto_link = f"mailto:{row['email']}?subject={oggetto}&body={corpo}"
                        st.link_button("✉️ INVIA SOLLECITO", mailto_link, use_container_width=True)
                    else:
                        st.button("Manca Email", disabled=True, key=f"dis_{row['id']}", use_container_width=True)
                
                st.markdown("<hr style='margin: 10px 0px; opacity: 0.1;'>", unsafe_allow_html=True)
                
        else:
            st.success("🎉 Grandioso! Tutte le aziende risultano in regola con i pagamenti.")
    else:
        st.info("Il database è attualmente vuoto.")

# ==========================================
# 05. COMPONENTE: EXPORT DOCUMENTI
# ==========================================
def render_export_documenti():
    st.markdown("<h2 style='color: #0033A0;'>📥 Centro Esportazione Documenti</h2>", unsafe_allow_html=True)
    st.markdown("Genera documenti impaginati globali o schede individuali basate sui dati attuali del network.")
    st.divider()

    df_attuali = leggi_soci()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("📚 **Catalogo Ufficiale**\n\nGenera l'impaginato completo.")
        if st.button("🚀 GENERA CATALOGO PDF", use_container_width=True):
            if not df_attuali.empty:
                with st.spinner("Generazione impaginato in corso..."):
                    from motore.pdf_engine import genera_catalogo
                    file_path = genera_catalogo(df_attuali) 
                    with open(file_path, "rb") as f:
                        st.download_button("⬇️ SCARICA CATALOGO", f, "Catalogo_Assafrica_2026.pdf", "application/pdf", use_container_width=True, type="primary")
            else: 
                st.warning("Database vuoto.")
                
    with c2:
        st.warning("📈 **Report Analitico**\n\nStatistiche e copertura geografica.")
        if st.button("📑 GENERA REPORT PDF", use_container_width=True):
            if not df_attuali.empty:
                with st.spinner("Analisi dati e generazione grafici..."):
                    from motore.report_generator import genera_report_dati
                    path_rep = genera_report_dati(df_attuali)
                    with open(path_rep, "rb") as f:
                        st.download_button("⬇️ SCARICA REPORT", f, "Report_Analisi_2026.pdf", "application/pdf", use_container_width=True, type="primary")
            else: 
                st.warning("Database vuoto.")
                
    with c3:
        st.success("📊 **Dati Grezzi (CSV)**\n\nEsportazione per Excel o CRM.")
        if st.button("💾 PREPARA LISTA EXCEL", use_container_width=True):
            if not df_attuali.empty:
                csv = df_attuali.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ SCARICA CSV", csv, "export_soci.csv", "text/csv", use_container_width=True, type="primary")
            else: 
                st.warning("Database vuoto.")

    st.divider()
    st.markdown("#### 📄 Esporta Scheda Singola Socio (One-Pager)")
    st.caption("Genera un documento di presentazione istituzionale in A4 per un singolo associato.")

    if not df_attuali.empty:
        nomi_soci = sorted(df_attuali['nome'].tolist())
        col_sel, col_btn = st.columns([3, 1])
        socio_nome = col_sel.selectbox("Seleziona l'Associato", nomi_soci, label_visibility="collapsed")
        
        if col_btn.button("✨ COMPILA ONE-PAGER", use_container_width=True):
            socio_data = df_attuali[df_attuali['nome'] == socio_nome].iloc[0]
            with st.spinner(f"Creazione scheda istituzionale per {socio_nome}..."):
                from motore.pdf_engine import genera_scheda_socio
                path_scheda = genera_scheda_socio(socio_data)
                if os.path.exists(path_scheda):
                    with open(path_scheda, "rb") as f:
                        st.download_button(
                            label=f"⬇️ SCARICA SCHEDA {socio_nome.upper()}",
                            data=f,
                            file_name=os.path.basename(path_scheda),
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )
    else:
        st.warning("Aggiungi dei soci nell'anagrafica per abilitare l'export delle schede.")

# ==========================================
# 06. COMPONENTE: MARKETING STUDIO
# ==========================================
def render_marketing_studio():
    st.markdown("<h2 style='color: #0033A0;'>🎨 Marketing Studio</h2>", unsafe_allow_html=True)
    st.markdown("Crea grafiche a 3 fasce come da standard istituzionali.")
    st.divider()

    col_form, col_preview = st.columns([1.2, 1])

    with col_form:
        with st.form("form_banner"):
            st.markdown("#### 1. Testi Principali")
            titolo_evento = st.text_input("Titolo Evento", "ENERGY, INFRASTRUCTURE & INDUSTRIAL SECURITY FORUM")
            sottotitolo = st.text_input("Sottotitolo", "From transit corridor to an integrated platform")
            data_luogo = st.text_input("Data e Luogo", "22 May 2026 | Belgrade")
            
            st.markdown("<br>#### 2. Immagini e Loghi Aggiuntivi", unsafe_allow_html=True)
            c_img1, c_img2 = st.columns(2)
            loghi_org_files = c_img1.file_uploader("Loghi Organizzatori", type=["png", "jpg"], accept_multiple_files=True)
            loghi_part_files = c_img2.file_uploader("Loghi Partner", type=["png", "jpg"], accept_multiple_files=True)
            sfondo_file = st.file_uploader("Grafica di Sfondo", type=["png", "jpg"])
            
            st.markdown("<br>#### 3. Impostazioni Formato", unsafe_allow_html=True)
            formato = st.selectbox("Formato Ottimizzato", ["LinkedIn Banner (1200x627)", "Instagram Post Quadrato (1080x1080)"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted_banner = st.form_submit_button("🚀 COMPONI GRAFICA SOCIAL", type="primary", use_container_width=True)
            
            if submitted_banner:
                from motore.marketing_engine import genera_banner
                conf = leggi_config()
                logo_inst = conf.get('logo_istituzionale', '')
                
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
                
                with st.spinner("Composizione grafica in corso..."):
                    path_img = genera_banner(
                        titolo_evento, sottotitolo, data_luogo, tipo, 
                        logo_inst=logo_inst, loghi_org=temp_orgs, loghi_partner=temp_parts, sfondo_dx=temp_sfondo
                    )
                    st.session_state['last_banner'] = path_img
                    st.toast("Grafica pronta per il download!", icon="✅")

    with col_preview:
        st.markdown("#### 👁️ Anteprima Risultato")
        if 'last_banner' in st.session_state and os.path.exists(st.session_state['last_banner']):
            st.image(st.session_state['last_banner'], use_container_width=True)
            with open(st.session_state['last_banner'], "rb") as file:
                st.download_button("⬇️ SCARICA IMMAGINE (JPG)", data=file, file_name="Locandina_Assafrica_2026.jpg", mime="image/jpeg", use_container_width=True, type="primary")
        else:
            st.markdown("<div style='height: 350px; display: flex; align-items: center; justify-content: center; background-color: #f0f2f6; border-radius: 10px; color: #888; text-align: center; padding: 20px;'>Compila i dati a sinistra e clicca su 'Componi Grafica' per visualizzare l'anteprima.</div>", unsafe_allow_html=True)

# ==========================================
# 07. COMPONENTE: CONFIGURAZIONE
# ==========================================
def render_configurazione():
    st.markdown("<h2 style='color: #0033A0;'>⚙️ Configurazione Sistema</h2>", unsafe_allow_html=True)
    st.markdown("Gestisci le impostazioni del profilo e i parametri globali dell'applicazione.")
    st.divider()

    # --- PARTE 1: PROFILO E SOCIAL ---
    st.markdown("#### 🏢 Impostazioni Profilo")
    conf = leggi_config()

    with st.form("config_form"):
        col1, col2 = st.columns(2)
        nome_ass = col1.text_input("Nome Associazione", value=conf.get('nome_associazione', 'Assafrica'))
        email_ass = col1.text_input("Email Contatto", value=conf.get('email_contatto', ''))
        indirizzo_ass = col2.text_input("Sede Legale", value=conf.get('indirizzo', ''))
        
        st.markdown("<br>**🌐 Web & Social Media Ufficiali**", unsafe_allow_html=True)
        c_s1, c_s2 = st.columns(2)
        sito_web = c_s1.text_input("Sito Web Ufficiale", value=conf.get('sito_web', 'www.assafrica.it'))
        linkedin = c_s2.text_input("LinkedIn", value=conf.get('linkedin', ''))
        facebook = c_s1.text_input("Facebook", value=conf.get('facebook', ''))
        instagram = c_s2.text_input("Instagram", value=conf.get('instagram', ''))
        youtube = c_s1.text_input("YouTube", value=conf.get('youtube', ''))
        
        st.markdown("<br>**🖼️ Gestione Loghi Istituzionali**", unsafe_allow_html=True)
        c_l1, c_l2 = st.columns(2)
        logo_inst = c_l1.file_uploader("Logo per sfondo CHIARO (Standard)", type=["png", "jpg", "jpeg"])
        logo_neg = c_l2.file_uploader("Logo per sfondo SCURO (Bianco/Negative)", type=["png", "jpg", "jpeg"])
        
        if st.form_submit_button("💾 SALVA PROFILO E SOCIAL", type="primary", use_container_width=True):
            path_std = conf.get('logo_istituzionale', '')
            path_neg = conf.get('logo_negativo', '')
            
            if not os.path.exists("media/loghi_soci"): os.makedirs("media/loghi_soci")
            
            if logo_inst:
                ext_std = logo_inst.name.split('.')[-1].lower()
                path_std = f"media/loghi_soci/LOGO_STD.{ext_std}"
                with open(path_std, "wb") as f:
                    f.write(logo_inst.getbuffer())
            
            if logo_neg:
                ext_neg = logo_neg.name.split('.')[-1].lower()
                path_neg = f"media/loghi_soci/LOGO_NEG.{ext_neg}"
                with open(path_neg, "wb") as f:
                    f.write(logo_neg.getbuffer())
            
            salva_config(nome_ass, path_std, path_neg, indirizzo_ass, email_ass, sito_web, linkedin, facebook, instagram, youtube)
            st.toast("Profilo, Social e loghi salvati correttamente!", icon="✅")
            st.rerun()

    st.divider()

    # --- PARTE 2: SETTORI DINAMICI ---
    st.markdown("#### 🏷️ Gestione Settori Merceologici")
    st.caption("Aggiungi o rimuovi le voci che appariranno nei menu a tendina in tutta l'applicazione.")
    
    categorie_attuali = ottieni_categorie()

    col_add, col_rem = st.columns([1, 1])

    with col_add:
        st.info("**Aggiungi Settore**")
        nuovo_settore = st.text_input("Nome del nuovo settore", placeholder="Es. FARMACEUTICA", label_visibility="collapsed").strip().upper()
        
        if st.button("➕ AGGIUNGI SETTORE", use_container_width=True):
            if nuovo_settore and nuovo_settore not in categorie_attuali:
                categorie_attuali.append(nuovo_settore)
                salva_categorie(sorted(categorie_attuali))
                st.toast(f"Settore '{nuovo_settore}' aggiunto!", icon="✅")
                st.rerun()
            elif nuovo_settore in categorie_attuali:
                st.warning("Questo settore esiste già.")

    with col_rem:
        st.warning("**Rimuovi Settore**")
        if categorie_attuali:
            settore_da_rimuovere = st.selectbox("Seleziona settore da eliminare", categorie_attuali, label_visibility="collapsed")
            if st.button("🗑️ ELIMINA SETTORE", use_container_width=True):
                categorie_attuali.remove(settore_da_rimuovere)
                salva_categorie(categorie_attuali)
                st.toast(f"Settore rimosso!", icon="🗑️")
                st.rerun()

# ==========================================
# 08. COMPONENTE: CENTRO RISORSE (KIT DOCUMENTI)
# ==========================================
def render_risorse():
    st.markdown("<h2 style='color: #0033A0;'>📚 Centro Risorse & Kit Documenti</h2>", unsafe_allow_html=True)
    st.markdown("Accedi ai materiali istituzionali o carica nuovi documenti direttamente nel cloud locale.")
    st.divider()

    # 1. Setup Cartelle Dinamiche
    base_dir = "risorse"
    cat_dirs = {
        "Primo Contatto": os.path.join(base_dir, "contatto"),
        "Presentazioni & Media": os.path.join(base_dir, "media"),
        "Modulistica Amministrativa": os.path.join(base_dir, "moduli")
    }
    
    for path in cat_dirs.values():
        if not os.path.exists(path):
            os.makedirs(path)

    # 2. Modulo di Caricamento (Upload)
    with st.expander("☁️ Carica un nuovo documento nella libreria", expanded=False):
        c_file, c_cat, c_btn = st.columns([2, 1, 1])
        
        nuovo_file = c_file.file_uploader("Seleziona il file dal tuo Mac", label_visibility="collapsed")
        categoria = c_cat.selectbox("Scegli il raccoglitore", list(cat_dirs.keys()), label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if c_btn.button("💾 SALVA IN ARCHIVIO", type="primary", use_container_width=True):
            if nuovo_file is not None:
                percorso_salvataggio = os.path.join(cat_dirs[categoria], nuovo_file.name)
                with open(percorso_salvataggio, "wb") as f:
                    f.write(nuovo_file.getbuffer())
                st.toast(f"File '{nuovo_file.name}' salvato in {categoria}!", icon="✅")
                st.rerun() 
            else:
                st.warning("⚠️ Seleziona prima un file da caricare.")

    st.write("")

    # 3. Visualizzazione Dinamica dei File
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### 🤝 Kit Primo Contatto")
            file_contatto = os.listdir(cat_dirs["Primo Contatto"])
            file_contatto = [f for f in file_contatto if not f.startswith('.')]
            
            if file_contatto:
                for f in file_contatto:
                    c_t, c_b = st.columns([3, 1])
                    c_t.write(f"📄 {f}")
                    path = os.path.join(cat_dirs["Primo Contatto"], f)
                    with open(path, "rb") as file_data:
                        c_b.download_button("Scarica", file_data, file_name=f, key=f"dl_c_{f}", use_container_width=True)
            else:
                st.caption("Nessun documento presente. Caricalo dal pannello in alto.")

    with col2:
        with st.container(border=True):
            st.markdown("#### 📢 Presentazioni & Media")
            file_media = os.listdir(cat_dirs["Presentazioni & Media"])
            file_media = [f for f in file_media if not f.startswith('.')]
            
            if file_media:
                for f in file_media:
                    c_t, c_b = st.columns([3, 1])
                    c_t.write(f"🎬 {f}")
                    path = os.path.join(cat_dirs["Presentazioni & Media"], f)
                    with open(path, "rb") as file_data:
                        c_b.download_button("Scarica", file_data, file_name=f, key=f"dl_m_{f}", use_container_width=True)
            else:
                st.caption("Nessun documento presente. Caricalo dal pannello in alto.")

    st.write("")
    with st.container(border=True):
        st.markdown("#### 📝 Modulistica Amministrativa")
        file_moduli = os.listdir(cat_dirs["Modulistica Amministrativa"])
        file_moduli = [f for f in file_moduli if not f.startswith('.')]
        
        if file_moduli:
            col_mod = st.columns(3)
            idx = 0
            for f in file_moduli:
                path = os.path.join(cat_dirs["Modulistica Amministrativa"], f)
                with open(path, "rb") as file_data:
                    col_mod[idx % 3].download_button(f"📑 {f}", file_data, file_name=f, key=f"dl_mod_{f}", use_container_width=True)
                idx += 1
        else:
            st.caption("Nessun modulo presente. Caricalo dal pannello in alto.")
            
# ==========================================
# 09. COMPONENTE: FOOTER BARRA LATERALE
# ==========================================
def render_sidebar_footer():
    from motore.database_manager import leggi_config
    conf = leggi_config()
    nome_ass = conf.get('nome_associazione', 'Assafrica')
    
    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/09_Configurazione.py", label="Impostazioni Sistema", icon="⚙️")
    st.sidebar.caption(f"© 2026 {nome_ass} - Enterprise Edition")