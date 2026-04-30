import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import os
import urllib.request
import ssl

def get_mappa_locale():
    """Scarica il file GeoJSON in locale la prima volta, bypassando blocchi SSL"""
    file_path = "world-countries.json"
    
    # Se il file non esiste sul computer, lo scarichiamo in modo forzato
    if not os.path.exists(file_path):
        url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
        
        # Creiamo un contesto che ignora i controlli SSL restrittivi
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        try:
            with urllib.request.urlopen(url, context=ctx) as response, open(file_path, 'wb') as out_file:
                out_file.write(response.read())
        except Exception as e:
            st.error(f"Errore di rete critico: Impossibile recuperare la mappa. Dettaglio: {e}")
            return url # Fallback estremo all'URL originale
            
    return file_path

def render_mappa(df):
    # CSS per pulire ulteriormente i margini e rendere le card più snelle
    st.markdown("""
        <style>
        .stDataFrame {border: none !important;}
        .compact-card {
            padding: 8px 12px; 
            border-radius: 6px; 
            border-left: 4px solid #004a99; 
            background-color: #fcfcfc; 
            margin-bottom: 6px;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
        }
        .compact-card h5 { margin: 0; color: #004a99; font-size: 1rem; }
        .compact-card p { margin: 0; font-size: 0.8rem; color: #666; }
        .compact-card a { font-size: 0.75rem; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("🌍 Network Explorer | Business Community")
    
    # 1. PREPARAZIONE DATI
    PAESI_AFRICA_LIST = [
        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Camerun", "Capo Verde", 
        "Ciad", "Comore", "Costa d'Avorio", "Egitto", "Eritrea", "Eswatini", "Etiopia", "Gabon", 
        "Gambia", "Ghana", "Gibuti", "Guinea", "Guinea Equatoriale", "Guinea-Bissau", "Kenya", 
        "Lesotho", "Liberia", "Libia", "Madagascar", "Malawi", "Mali", "Marocco", "Mauritania", 
        "Mauritius", "Mozambico", "Namibia", "Niger", "Nigeria", "Repubblica Centrafricana", 
        "Repubblica del Congo", "Repubblica Democratica del Congo", "Ruanda", "Sahara Occidentale", 
        "Senegal", "Seychelles", "Sierra Leone", "Somalia", "Sudafrica", "Sudan", "Sudan del Sud", 
        "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
    ]

    conteggio = {p: 0 for p in PAESI_AFRICA_LIST}
    for _, row in df.iterrows():
        sede = str(row.get('sede', ''))
        target = PAESI_AFRICA_LIST if sede == "Tutta l'Africa" else [p.strip() for p in sede.split(',') if p.strip() in PAESI_AFRICA_LIST]
        for p in target:
            conteggio[p] += 1
    df_counts = pd.DataFrame(list(conteggio.items()), columns=['name', 'soci'])

    col_left, col_right = st.columns([0.65, 0.35])

    # Otteniamo il percorso del file locale (o lo scarichiamo se è la prima volta)
    geojson_data = get_mappa_locale()

    with col_left:
        # 2. MAPPA FISSA (No zoom, No dragging)
        m = folium.Map(
            location=[2.0, 18.0], 
            zoom_start=3.2, 
            tiles="CartoDB positron",
            zoom_control=False,     # Rimuove i tasti + e -
            scrollWheelZoom=False,  # Disabilita lo zoom con la rotellina
            dragging=False          # Blocca il trascinamento
        )

        folium.Choropleth(
            geo_data=geojson_data, # Usiamo il file locale sicuro
            data=df_counts,
            columns=["name", "soci"],
            key_on="feature.properties.name",
            fill_color="Blues", 
            fill_opacity=0.7,
            line_opacity=0.2,
            nan_fill_color="#f8f9fa",
            highlight=True,
        ).add_to(m)

        # Layer per il click
        folium.GeoJson(
            geojson_data, # Usiamo il file locale sicuro
            name="geojson",
            style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent', 'weight': 0},
            tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Stato:'], localize=True)
        ).add_to(m)

        map_output = st_folium(m, width=720, height=520, key="mappa_fissa")

    with col_right:
        # 3. PANNELLO SCHEDE COMPATTE
        paese_selezionato = None
        if map_output and map_output.get("last_active_drawing"):
            paese_selezionato = map_output["last_active_drawing"]["properties"]["name"]

        if paese_selezionato and paese_selezionato in PAESI_AFRICA_LIST:
            st.markdown(f"#### 📍 {paese_selezionato}")
            
            mask = df.apply(lambda r: paese_selezionato in str(r['sede']) or str(r['sede']) == "Tutta l'Africa", axis=1)
            df_filtrato = df[mask]
            
            # Contenitore ad altezza fissa uguale alla mappa per simmetria
            container = st.container(height=460)
            with container:
                if not df_filtrato.empty:
                    for _, soci in df_filtrato.iterrows():
                        st.markdown(f"""
                        <div class="compact-card">
                            <h5>{soci['nome']}</h5>
                            <p><b>{soci['categoria']}</b> | {soci['referente']}</p>
                            <div style="margin-top:4px;">
                                <a href="mailto:{soci['email']}" style="color:#d9534f; margin-right:10px;">📧 Email</a>
                                <a href="{soci['sito'] if str(soci['sito']).startswith('http') else 'https://'+str(soci['sito'])}" target="_blank" style="color:#004a99;">🌐 Web</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Nessun socio registrato in quest'area.")
        else:
            st.info("👈 Seleziona uno stato sulla mappa per i dettagli.")
            st.markdown("""
                <div style="text-align:center; opacity:0.5; margin-top:50px;">
                    <img src="https://img.icons8.com/ios/100/africa.png" width="80">
                    <p>Network Assafrica 2026</p>
                </div>
            """, unsafe_allow_html=True)