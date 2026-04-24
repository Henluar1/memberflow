import streamlit as st
from streamlit_folium import st_folium
import folium

# Dizionario coordinate centrali per i paesi africani (per velocità e precisione)
COORDS_AFRICA = {
    "Algeria": [28.0339, 1.6596], "Angola": [-11.2027, 17.8739], "Benin": [9.3077, 2.3158],
    "Botswana": [-22.3285, 24.6849], "Burkina Faso": [12.2383, -1.5616], "Burundi": [-3.3731, 29.9189],
    "Camerun": [7.3697, 12.3547], "Capo Verde": [16.002, -24.0131], "Ciad": [15.4542, 18.7322],
    "Comore": [-11.6455, 43.3333], "Costa d'Avorio": [7.54, -5.5471], "Egitto": [26.8206, 30.8025],
    "Eritrea": [15.1794, 39.7823], "Eswatini": [-26.5225, 31.4659], "Etiopia": [9.145, 40.4897],
    "Gabon": [-0.8037, 11.6094], "Gambia": [13.4432, -15.3101], "Ghana": [7.9465, -1.0232],
    "Gibuti": [11.8251, 42.5903], "Guinea": [9.9456, -9.6966], "Guinea Equatoriale": [1.6508, 10.2679],
    "Guinea-Bissau": [11.8037, -15.1804], "Kenya": [-0.0236, 37.9062], "Lesotho": [-29.61, 28.2336],
    "Liberia": [6.4281, -9.4295], "Libia": [26.3351, 17.2283], "Madagascar": [-18.7669, 46.8691],
    "Malawi": [-13.2543, 34.3015], "Mali": [17.5707, -3.9962], "Marocco": [31.7917, -7.0926],
    "Mauritania": [21.0079, -10.9408], "Mauritius": [-20.3484, 57.5522], "Mozambico": [-18.6657, 35.5296],
    "Namibia": [-22.9576, 18.4904], "Niger": [17.6078, 8.0817], "Nigeria": [9.082, 8.6753],
    "Repubblica Centrafricana": [6.6111, 20.9394], "Repubblica del Congo": [-0.228, 15.8277],
    "Repubblica Democratica del Congo": [-4.0383, 21.7587], "Ruanda": [-1.9403, 29.8739],
    "Sahara Occidentale": [24.2155, -12.8858], "Senegal": [14.4974, -14.4524], "Seychelles": [-4.6796, 55.492],
    "Sierra Leone": [8.4606, -11.7799], "Somalia": [5.1521, 46.1996], "Sudafrica": [-30.5595, 22.9375],
    "Sudan": [12.8628, 30.2176], "Sudan del Sud": [6.877, 31.307], "Tanzania": [-6.369, 34.8888],
    "Togo": [8.6195, 0.8248], "Tunisia": [33.8869, 9.5375], "Uganda": [1.3733, 32.2903],
    "Zambia": [-13.1339, 27.8493], "Zimbabwe": [-19.0154, 29.1549]
}

def render_mappa(df):
    st.subheader("🌍 Mappa Operatività Associati")
    
    # Centro della mappa sull'Africa
    m = folium.Map(location=[2.0, 16.0], zoom_start=3, tiles="CartoDB positron")

    for i, row in df.iterrows():
        paesi_stringa = row.get('sede', '')
        if not paesi_stringa:
            continue
            
        # Determiniamo la lista dei paesi in cui l'azienda opera
        if paesi_stringa == "Tutta l'Africa":
            paesi_da_disegnare = list(COORDS_AFRICA.keys())
        else:
            paesi_da_disegnare = paesi_stringa.split(",")

        # Colore basato sul pagamento
        colore = "blue" if row['pagato'] == "Pagato" else "orange"

        for paese in paesi_da_disegnare:
            paese = paese.strip()
            if paese in COORDS_AFRICA:
                # Usiamo CircleMarker per un look più moderno e pulito
                folium.CircleMarker(
                    location=COORDS_AFRICA[paese],
                    radius=6,
                    color=colore,
                    fill=True,
                    fill_color=colore,
                    fill_opacity=0.7,
                    popup=folium.Popup(f"""
                        <div style='width: 200px;'>
                            <b>{row['nome']}</b><br>
                            <i>{row['categoria']}</i><br><br>
                            Presenza in: {paese}<br>
                            Stato: {row['pagato']}
                        </div>
                    """),
                    tooltip=f"{row['nome']} - {paese}"
                ).add_to(m)

    # Renderizzazione della mappa
    st_folium(m, width=1300, height=600)
    
    st.caption("🔵 Aziende in regola con i pagamenti | 🟠 Aziende con pagamenti in attesa")