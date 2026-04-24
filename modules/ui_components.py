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

# Categorie aggiornate basate sul Catalogo Reale 2025
CATEGORIE_REAL = [
    "ENERGIA & AMBIENTE", "MACCHINARI & IMPIANTI", "ICT & DIGITALE", 
    "EDILIZIA & INFRASTRUTTURE", "AGROALIMENTARE", "LOGISTICA & TRASPORTI", 
    "CHIMICA & GOMMA", "SERVIZI ALLE IMPRESE", "BANCHE", "ALTRO"
]

def render_form_inserimento():
    st.subheader("📝 Registra nuova Azienda dal Catalogo")
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
            
            st.write("---")
            st.write("🌍 **Operatività in Africa**")
            tutto_continente = st.toggle("Opera in tutto il continente (Pan-Africana)")
            paesi_selezionati = ["Tutta l'Africa"] if tutto_continente else st.multiselect("Seleziona Paesi specifici", PAESI_AFRICA)
            
            st.write("---")
            st.write("🖼️ **Logo Aziendale**")
            logo_file = st.file_uploader("Carica file locale (PNG/JPG)", type=["png", "jpg", "jpeg"])
            
            desc = st.text_area("Descrizione attività")
            
            if st.form_submit_button("SALVA NEL DATABASE"):
                if nome and paesi_selezionati:
                    path_finale = ""
                    if logo_file:
                        if not os.path.exists("loghi_soci"): os.makedirs("loghi_soci")
                        path_finale = f"loghi_soci/{nome.replace(' ', '_').upper()}.png"
                        Image.open(logo_file).save(path_finale)
                    
                    stringa_paesi = ",".join(paesi_selezionati)
                    aggiungi_socio(nome, cat, ref, mail, web, desc, path_finale, pagato, stringa_paesi)
                    st.success(f"Azienda {nome} aggiunta con successo!")
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
                            "", # I loghi si caricano dopo via Gestione
                            "Pagato", 
                            get_smart_val(row, ['sede', 'paesi', 'operatività'], "Tutta l'Africa")
                        )
                        progress_bar.progress((i + 1) / len(df_import))
                    st.success("Importazione anagrafiche completata!")
                    st.rerun()

def render_gestione():
    df = leggi_soci()
    if not df.empty:
        st.subheader("📋 Gestione Anagrafiche e Loghi")
        cerca = st.text_input("🔍 Cerca socio", placeholder="Es: Eni, Energia...")
        if cerca:
            df = df[df['nome'].str.contains(cerca, case=False) | df['categoria'].str.contains(cerca, case=False)]
        
        for i, row in df.iterrows():
            with st.expander(f"🏢 {row['nome']} ({row['categoria']})"):
                c1, c2 = st.columns(2)
                new_nome = c1.text_input("Ragione Sociale", value=row['nome'], key=f"n_{row['id']}")
                idx_cat = CATEGORIE_REAL.index(row['categoria']) if row['categoria'] in CATEGORIE_REAL else 0
                new_cat = c1.selectbox("Settore", CATEGORIE_REAL, index=idx_cat, key=f"c_{row['id']}")
                new_ref = c1.text_input("Referente Assafrica", value=row['referente'], key=f"r_{row['id']}")
                new_mail = c2.text_input("Email", value=row['email'], key=f"e_{row['id']}")
                new_web = c2.text_input("Sito Web", value=row['sito'], key=f"w_{row['id']}")
                new_pag = c2.selectbox("Stato", ["Pagato", "In attesa"], 
                                       index=0 if row['pagato'] == "Pagato" else 1, key=f"p_{row['id']}")
                
                st.write("---")
                st.write("🖼️ **Gestione Logo**")
                col_img, col_edit = st.columns([0.3, 0.7])
                
                logo_path = row['logo_path']
                if logo_path and os.path.exists(logo_path):
                    col_img.image(logo_path, width=120)
                else:
                    col_img.warning("Nessun logo caricato")
                
                new_logo_file = col_edit.file_uploader("Sostituisci file logo", type=["png", "jpg", "jpeg"], key=f"up_{row['id']}")
                
                st.write("---")
                current_paesi = str(row['sede']).split(",") if row['sede'] else []
                is_all_africa = "Tutta l'Africa" in current_paesi
                togg = st.toggle("Opera in tutta l'Africa", value=is_all_africa, key=f"togg_{row['id']}")
                
                if togg:
                    new_paesi_str = "Tutta l'Africa"
                else:
                    defaults = [p.strip() for p in current_paesi if p.strip() in PAESI_AFRICA]
                    sel = st.multiselect("Modifica Paesi", PAESI_AFRICA, default=defaults, key=f"ms_{row['id']}")
                    new_paesi_str = ",".join(sel)
                
                new_desc = st.text_area("Descrizione attività", value=row['descrizione'], key=f"d_{row['id']}")
                
                b1, b2 = st.columns(2)
                if b1.button("💾 SALVA MODIFICHE", key=f"save_{row['id']}", use_container_width=True):
                    path_finale = logo_path
                    if new_logo_file:
                        if not os.path.exists("loghi_soci"): os.makedirs("loghi_soci")
                        path_finale = f"loghi_soci/{new_nome.replace(' ', '_').upper()}.png"
                        Image.open(new_logo_file).save(path_finale)
                        
                    aggiorna_socio(row['id'], new_nome, new_cat, new_ref, new_mail, new_web, new_desc, path_finale, new_pag, new_paesi_str)
                    st.success("Dati aggiornati con successo!")
                    st.rerun()
                
                if b2.button("🗑️ ELIMINA AZIENDA", key=f"del_{row['id']}", use_container_width=True):
                    elimina_socio(row['id'])
                    st.rerun()
    else:
        st.info("Database vuoto.")

def render_analytics():
    # ... (Restra uguale, mostra le Dashboard di Business Intelligence)
    df = leggi_soci()
    if not df.empty:
        st.subheader("📊 Business Intelligence & Macro-Trend Africa")
        
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
