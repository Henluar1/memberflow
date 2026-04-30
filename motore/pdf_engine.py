import os
import requests
import urllib.request
from fpdf import FPDF
from datetime import datetime
from motore.database_manager import leggi_config

# Colori ufficiali istituzionali
BLUE_ASSAFRICA = (0, 45, 90)
GOLD_ASSAFRICA = (184, 151, 93)

def pulisci_testo_pdf(testo):
    """Pulisce il testo dai caratteri Unicode non supportati dal font standard Helvetica."""
    if not testo:
        return ""
    testo = str(testo)
    
    # Sostituzioni intelligenti per i caratteri Word/Web più comuni
    replacements = {
        "’": "'", "‘": "'", "`": "'",
        "“": '"', "”": '"', "«": '"', "»": '"',
        "–": "-", "—": "-", "…": "...", 
        "•": "-", "\u2022": "-", "\u2018": "'", 
        "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "€": "Euro", "®": "(R)", "™": "(TM)", "©": "(C)"
    }
    
    for bad, good in replacements.items():
        testo = testo.replace(bad, good)
        
    # Forza la conversione in Latin-1 ignorando i caratteri alieni rimasti
    return testo.encode('latin-1', 'ignore').decode('latin-1')

def scarica_icone_globali():
    """Scarica icone social bianche e icone settore standard se mancanti."""
    # Cartelle Sicure
    folders = ["media/icons/social", "media/icons/settori"]
    for f in folders:
        if not os.path.exists(f):
            os.makedirs(f)
    
    # 1. URL Social (PNG bianche per footer blu)
    social_urls = {
        "linkedin": "https://img.icons8.com/ios-filled/50/ffffff/linkedin.png",
        "facebook": "https://img.icons8.com/ios-filled/50/ffffff/facebook-new.png",
        "instagram": "https://img.icons8.com/ios-filled/50/ffffff/instagram-new.png",
        "youtube": "https://img.icons8.com/ios-filled/50/ffffff/youtube-play.png",
        "web": "https://img.icons8.com/ios-filled/50/ffffff/globe.png"
    }
    
    # 2. Icona Settore di Default (se l'utente non ha caricato quella specifica)
    sector_urls = {
        "ALTRO": "https://img.icons8.com/ios-filled/50/000000/organization.png" # Icona nera standard
    }
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for name, url in social_urls.items():
        path = os.path.join("media/icons/social", f"{name}.png")
        if not os.path.exists(path):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
                    out_file.write(response.read())
            except: pass
            
    for name, url in sector_urls.items():
        path = os.path.join("media/icons/settori", f"{name}.png")
        if not os.path.exists(path):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
                    out_file.write(response.read())
            except: pass

def ottieni_percorso_icona_settore(categoria):
    """Cerca un'icona specifica per la categoria merceologica."""
    cat_clean = "".join(x for x in categoria if x.isalnum() or x in " &-").upper()
    percorso_specifico = f"media/icons/settori/{cat_clean}.png"
    
    if os.path.exists(percorso_specifico):
        return percorso_specifico
    return "media/icons/settori/ALTRO.png" # Default

class CatalogoPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_draw_color(*GOLD_ASSAFRICA)
            self.set_line_width(0.4)
            self.line(10, 15, 287, 15)
            
    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            conf = leggi_config()
            nome_ass = pulisci_testo_pdf(conf.get('nome_associazione', 'ASSAFRICA'))
            info = f"{nome_ass} | Business Community Network 2026"
            self.cell(0, 10, f"{info}   -   Pagina {self.page_no()}", 0, 0, "C")

def genera_catalogo(df_soci, output_name="Catalogo_Associati_2026.pdf"):
    pdf = CatalogoPDF(orientation='L', unit='mm', format='A4')
    pdf.set_margins(10, 20, 10)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    conf = leggi_config()
    logo_inst = conf.get('logo_istituzionale', '')
    nome_ass = pulisci_testo_pdf(conf.get('nome_associazione', 'CONFINDUSTRIA ASSAFRICA & MEDITERRANEO'))

    # --- 1. COVER PAGE ---
    pdf.add_page()
    
    pdf.set_fill_color(*BLUE_ASSAFRICA)
    pdf.rect(0, 0, 95, 210, 'F')
    
    pdf.set_fill_color(*GOLD_ASSAFRICA)
    pdf.rect(95, 0, 2.5, 210, 'F')
    
    if logo_inst and os.path.exists(logo_inst):
        w_logo = 95
        x_logo = 97.5 + (297 - 97.5 - w_logo) / 2
        pdf.image(logo_inst, x=x_logo, y=75, w=w_logo) 
    
    pdf.set_text_color(255, 255, 255)
    
    pdf.set_xy(10, 85)
    pdf.set_font("helvetica", "B", 32)
    pdf.multi_cell(80, 12, "BUSINESS\nCOMMUNITY", align="L")
    
    pdf.set_xy(10, 112)
    pdf.set_font("helvetica", "", 28)
    pdf.cell(80, 15, "2026", ln=True, align="L")
    
    pdf.set_xy(10, 180)
    pdf.set_font("helvetica", "B", 10)
    pdf.multi_cell(75, 5, nome_ass.upper(), align="L")

    # --- 2. INDICE ---
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 22)
    pdf.set_text_color(*BLUE_ASSAFRICA)
    pdf.cell(0, 15, "INDICE DELLE AZIENDE", ln=True, align="L")
    
    df_soci = df_soci.sort_values(by=['categoria', 'nome'])
    categorie = df_soci['categoria'].unique()
    
    links = {}
    current_p = 3
    for cat in categorie:
        links[cat] = pdf.add_link()
        pdf.set_font("helvetica", "", 12)
        pdf.set_text_color(60, 60, 60)
        cat_pulita = pulisci_testo_pdf(cat)
        pdf.write(10, cat_pulita.upper(), link=links[cat])
        
        x_curr = pdf.get_x() + 2
        pdf.set_draw_color(200, 200, 200)
        for i in range(int(x_curr), 275, 5):
            pdf.line(i, pdf.get_y() + 7, i + 1, pdf.get_y() + 7)
            
        pdf.set_x(275)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(10, 10, str(current_p), align="R", ln=True)
        
        num_soci = len(df_soci[df_soci['categoria'] == cat])
        current_p += (num_soci + 5) // 6

    # --- 3. SCHEDE AZIENDALI ---
    current_cat = None
    i_cat = 0
    box_w, box_h = 88, 76 
    margin_x, margin_y_start = 12, 35 

    for _, row in df_soci.iterrows():
        if row['categoria'] != current_cat:
            current_cat = row['categoria']
            page_in_cat = 1
            i_cat = 0
            pdf.add_page()
            pdf.set_link(links[current_cat])
        
        if i_cat > 0 and i_cat % 6 == 0:
            pdf.add_page()
            page_in_cat += 1
            
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(*GOLD_ASSAFRICA)
        pdf.set_xy(12, 18)
        cat_pulita = pulisci_testo_pdf(current_cat)
        pdf.cell(0, 10, f"{cat_pulita.upper()} / {page_in_cat}", ln=True)

        pos_in_page = i_cat % 6
        col, fila = pos_in_page % 3, pos_in_page // 3
        x, y = margin_x + (col * (box_w + 6)), margin_y_start + (fila * (box_h + 8))
        
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(230, 230, 230)
        pdf.set_line_width(0.2)
        pdf.rect(x, y, box_w, box_h, 'DF')
        
        nome_pulito = pulisci_testo_pdf(str(row['nome'])).upper()
        
        if row['logo_path'] and os.path.exists(str(row['logo_path'])):
            pdf.image(str(row['logo_path']), x=x + (box_w-45)/2, y=y + 6, w=45)
        else:
            pdf.set_xy(x + 5, y + 15)
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(*BLUE_ASSAFRICA)
            pdf.multi_cell(box_w - 10, 5, nome_pulito, align="C")

        pdf.set_xy(x + 5, y + 35)
        pdf.set_font("helvetica", "", 8.5)
        pdf.set_text_color(50, 50, 50)
        
        testo = pulisci_testo_pdf(str(row['descrizione']))
        if len(testo) > 165: testo = testo[:162] + "..."
        pdf.multi_cell(box_w - 10, 4.2, testo, align="C")

        pdf.set_xy(x + 6, y + 56)
        pdf.set_font("helvetica", "B", 8)
        pdf.set_text_color(*BLUE_ASSAFRICA)
        ref_pulito = pulisci_testo_pdf(str(row['referente']))
        pdf.cell(box_w - 12, 4.5, f"Ref: {ref_pulito}", ln=True)
        
        pdf.set_font("helvetica", "", 8)
        pdf.set_x(x + 6)
        mail_pulita = pulisci_testo_pdf(str(row['email'])).lower()
        pdf.cell(box_w - 12, 4, mail_pulita, ln=True)
        
        pdf.set_x(x + 6)
        pdf.set_text_color(*GOLD_ASSAFRICA)
        sito_pulito = pulisci_testo_pdf(str(row['sito'])).lower()
        pdf.cell(box_w - 12, 4, sito_pulito, align="L")
        
        i_cat += 1
    
    if not os.path.exists("exports"): os.makedirs("exports")
    final_path = f"exports/{output_name}"
    pdf.output(final_path)
    return final_path

# ==========================================
# NUOVO DESIGN ELITE: WELCOME NEW MEMBER
# Integrato con Foto Copertina e Simboli Categoria
# ==========================================
def genera_scheda_socio(socio_data):
    """Genera una locandina 'Welcome Member' di altissimo livello visivo."""
    
    try:
        scarica_icone_globali()
    except:
        pass 

    conf = leggi_config()
    nome_ass = pulisci_testo_pdf(conf.get('nome_associazione', 'CONFINDUSTRIA ASSAFRICA'))
    logo_ass_std = conf.get('logo_istituzionale', '')
    sito_web = pulisci_testo_pdf(conf.get('sito_web', 'www.assafrica.it'))

    nome_socio = pulisci_testo_pdf(str(socio_data.get('nome', 'Azienda')).upper())
    categoria_socio = pulisci_testo_pdf(str(socio_data.get('categoria', 'ALTRO')))
    logo_socio = str(socio_data.get('logo_path', ''))
    
    cover_socio = str(socio_data.get('immagine_copertina_path', '')) if 'immagine_copertina_path' in socio_data else ''

    desc_lunga = str(socio_data.get('descrizione_lunga', ''))
    desc_breve = str(socio_data.get('descrizione', ''))
    testo_grezzo = desc_lunga if (len(desc_lunga) > 10) else desc_breve
    testo_presentazione = pulisci_testo_pdf(testo_grezzo)

    if not testo_presentazione.strip():
        testo_presentazione = "Nessuna descrizione disponibile."

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)

    BLU = BLUE_ASSAFRICA
    ORO = GOLD_ASSAFRICA
    BIANCO = (255, 255, 255)
    GRIGIO = (60, 60, 60)

    # --- FASE 1: SFONDO IMMAGINE ---
    if cover_socio and os.path.exists(cover_socio):
        try:
            pdf.image(cover_socio, x=0, y=0, w=210, h=297, type='', link='')
        except:
            pdf.set_fill_color(*BIANCO)
            pdf.rect(0, 0, 210, 297, 'F')
    else:
        pdf.set_fill_color(*BIANCO)
        pdf.rect(0, 0, 210, 297, 'F')

    # --- FASE 2: DESIGN A BLOCCHI ---

    # -- BLOCCO 1: HEADER --
    h_header = 45
    pdf.set_fill_color(*BIANCO)
    pdf.rect(0, 0, 210, h_header, 'F')
    
    pdf.set_fill_color(*ORO)
    pdf.rect(0, h_header-1.5, 210, 1.5, 'F')

    pdf.set_font("helvetica", 'B', 36)
    pdf.set_text_color(*BLU)
    pdf.set_xy(15, 10)
    pdf.cell(100, 12, "Meet Our", ln=True)
    pdf.set_x(15)
    pdf.cell(100, 12, "New Member", ln=True)

    if logo_ass_std and isinstance(logo_ass_std, str) and os.path.exists(logo_ass_std):
        try:
            pdf.image(logo_ass_std, x=155, y=8, w=40)
        except: pass

    # -- BLOCCO 2: FASCIA CENTRALE --
    h_blue = 140
    y_blue = h_header
    pdf.set_fill_color(*BLU)
    pdf.rect(0, y_blue, 210, h_blue, 'F')

    pdf.set_font("helvetica", '', 16)
    pdf.set_text_color(*BIANCO)
    pdf.set_xy(15, y_blue + 10)
    pdf.cell(180, 8, f"Welcome to {nome_ass}", ln=True)

    pdf.set_font("helvetica", 'B', 36)
    pdf.set_xy(15, y_blue + 20)
    pdf.multi_cell(180, 14, nome_socio)

    x_logo_box = 15
    y_logo_box = y_blue + 55
    pdf.set_fill_color(*BIANCO)
    pdf.rect(x_logo_box, y_logo_box, 85, 55, 'F') 
    
    if logo_socio and isinstance(logo_socio, str) and os.path.exists(logo_socio):
        try:
            pdf.image(logo_socio, x=x_logo_box+5, y=y_logo_box+5, w=75, h=45, type='', link='')
        except: pass
    else:
        pdf.set_xy(x_logo_box+5, y_logo_box+15)
        pdf.set_font("helvetica", "B", 20)
        pdf.set_text_color(*BLU)
        pdf.multi_cell(75, 8, nome_socio, align="C")

    # ZONA CATEGORIA
    x_cat = x_logo_box + 85 + 10
    y_cat = y_logo_box + 10
    
    icon_cat_path = ottieni_percorso_icona_settore(categoria_socio)
    if os.path.exists(icon_cat_path):
        try:
            pdf.image(icon_cat_path, x=x_cat, y=y_cat, w=15)
        except: pass
        
    pdf.set_xy(x_cat + 20, y_cat + 2)
    pdf.set_font("helvetica", 'B', 18)
    pdf.set_text_color(*BIANCO)
    pdf.multi_cell(80, 10, categoria_socio.upper())

    # -- BLOCCO 3: DESCRIZIONE --
    y_desc = y_blue + h_blue + 10
    pdf.set_fill_color(*BIANCO)
    pdf.rect(15, y_desc, 180, 70, 'F') 
    
    pdf.set_draw_color(*ORO)
    pdf.set_line_width(0.8)
    pdf.rect(15, y_desc, 180, 70, 'D')

    pdf.set_xy(22, y_desc + 8)
    pdf.set_font("helvetica", '', 12)
    pdf.set_text_color(*GRIGIO)
    
    if len(testo_presentazione) > 700:
        testo_presentazione = testo_presentazione[:697] + "..."
        
    pdf.multi_cell(166, 7, testo_presentazione, align='J')

    # -- BLOCCO 4: FOOTER --
    y_footer = 270
    pdf.set_fill_color(*BLU)
    pdf.rect(0, y_footer, 210, 27, 'F')
    
    pdf.set_font("helvetica", 'B', 12)
    pdf.set_text_color(*BIANCO)
    pdf.set_xy(0, y_footer + 5)
    pdf.cell(210, 8, f"As {nome_ass} we look forward to a successful partnership!", align='C', ln=True)

    start_x = 20
    current_x = start_x
    y_social = y_footer + 14
    
    socials = {
        "youtube": conf.get('youtube', ''),
        "linkedin": conf.get('linkedin', ''),
        "facebook": conf.get('facebook', ''),
        "instagram": conf.get('instagram', ''),
        "web": sito_web
    }
    
    for name, link in socials.items():
        if link and str(link).strip() != "":
            icon_path = f"media/icons/social/{name}.png"
            if os.path.exists(icon_path):
                try:
                    pdf.image(icon_path, x=current_x, y=y_social, w=5)
                except: pass
                current_x += 7
                if name == "web":
                    pdf.set_xy(current_x, y_social + 1)
                    pdf.set_font("helvetica", "B", 10)
                    clean_url = str(link).replace('https://', '').replace('http://', '').strip('/')
                    pdf.cell(pdf.get_string_width(clean_url), 4, clean_url)
                    current_x += pdf.get_string_width(clean_url) + 5
                else:
                    current_x += 1

    # 4. Salvataggio ed Export
    if not os.path.exists("exports"):
        os.makedirs("exports")
        
    nome_file_pulito = "".join(x for x in nome_socio if x.isalnum() or x in " ").replace(' ', '_')
    path_export = f"exports/Welcome_{nome_file_pulito}.pdf"
    
    pdf.output(path_export)
    return path_export