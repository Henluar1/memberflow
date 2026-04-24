from fpdf import FPDF
import os
from datetime import datetime
from modules.database_manager import leggi_config

# Colori ufficiali istituzionali desunti dal PDF 2025
BLUE_ASSAFRICA = (0, 45, 90)
GOLD_ASSAFRICA = (184, 151, 93)

class CatalogoPDF(FPDF):
    def header(self):
        # Disegna una linea oro sottile decorativa a partire dalla pagina 2
        if self.page_no() > 1:
            self.set_draw_color(*GOLD_ASSAFRICA)
            self.set_line_width(0.4)
            self.line(10, 15, 287, 15)
            
    def footer(self):
        # Il footer compare solo dopo la copertina
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            conf = leggi_config()
            nome_ass = conf.get('nome_associazione', 'ASSAFRICA')
            info = f"{nome_ass} | Business Community Network 2026"
            self.cell(0, 10, f"{info}   -   Pagina {self.page_no()}", 0, 0, "C")

def genera_catalogo(df_soci, output_name="Catalogo_Associati_2026.pdf"):
    pdf = CatalogoPDF(orientation='L', unit='mm', format='A4')
    pdf.set_margins(10, 20, 10)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    conf = leggi_config()
    logo_inst = conf.get('logo_istituzionale', '')
    logo_neg = conf.get('logo_negativo', '')
    nome_ass = conf.get('nome_associazione', 'CONFINDUSTRIA ASSAFRICA & MEDITERRANEO')

    # --- 1. COVER PAGE (DESIGN REVISIONATO) ---
    pdf.add_page()
    
    # Sfondo: Fascia Blu a sinistra (allargata per miglior equilibrio)
    pdf.set_fill_color(*BLUE_ASSAFRICA)
    pdf.rect(0, 0, 110, 210, 'F')
    
    # Linea Oro di accento verticale
    pdf.set_fill_color(*GOLD_ASSAFRICA)
    pdf.rect(110, 0, 3, 210, 'F')
    
    # Logo Grande centrato nella sezione bianca (destra)
    # Area bianca utile: da 113mm a 297mm (larghezza 184mm)
    path_logo_cover = logo_neg if (logo_neg and os.path.exists(logo_neg)) else logo_inst
    if path_logo_cover and os.path.exists(path_logo_cover):
        w_logo = 90
        x_logo = 113 + (184 - w_logo) / 2
        pdf.image(path_logo_cover, x=x_logo, y=70, w=w_logo) 
    
    # Titoli sulla fascia Blu
    pdf.set_text_color(255, 255, 255)
    
    # BUSINESS COMMUNITY - Testo grande e Bold
    pdf.set_xy(15, 80)
    pdf.set_font("helvetica", "B", 42)
    pdf.multi_cell(90, 16, "BUSINESS\nCOMMUNITY", align="L")
    
    # 2026 - Testo Regular più leggero
    pdf.set_xy(15, 115)
    pdf.set_font("helvetica", "", 36)
    pdf.cell(90, 20, "2026", ln=True, align="L")
    
    # Nome Associazione in basso
    pdf.set_xy(15, 175)
    pdf.set_font("helvetica", "B", 12)
    pdf.multi_cell(85, 6, nome_ass.upper(), align="L")

    # --- 2. INDICE ---
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 22)
    pdf.set_text_color(*BLUE_ASSAFRICA)
    pdf.cell(0, 15, "INDICE DELLE AZIENDE", ln=True, align="L")
    
    df_soci = df_soci.sort_values(by=['categoria', 'nome'])
    categorie = df_soci['categoria'].unique()
    
    links = {}
    current_p = 3 # Pag 1: Cover, Pag 2: Indice, Schede partono da Pag 3
    for cat in categorie:
        links[cat] = pdf.add_link()
        pdf.set_font("helvetica", "", 12)
        pdf.set_text_color(60, 60, 60)
        pdf.write(10, cat.upper(), link=links[cat])
        
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
    spacing_x, spacing_y = 6, 8

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
            
        # Titolo Categoria e numerazione interna
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(*GOLD_ASSAFRICA)
        pdf.set_xy(12, 18) # Spostato leggermente per non toccare la linea oro
        pdf.cell(0, 10, f"{current_cat.upper()} / {page_in_cat}", ln=True)

        pos_in_page = i_cat % 6
        col = pos_in_page % 3
        fila = pos_in_page // 3
        x = margin_x + (col * (box_w + spacing_x))
        y = margin_y_start + (fila * (box_h + spacing_y))
        
        # Card pulita con bordo leggero
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(230, 230, 230)
        pdf.set_line_width(0.2)
        pdf.rect(x, y, box_w, box_h, 'DF')
        
        # Logo Azienda
        if row['logo_path'] and os.path.exists(row['logo_path']):
            # Centratura logo all'interno della card
            pdf.image(row['logo_path'], x=x + (box_w-45)/2, y=y + 6, w=45)
        else:
            pdf.set_xy(x + 5, y + 15)
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(*BLUE_ASSAFRICA)
            pdf.multi_cell(box_w - 10, 5, str(row['nome']).upper(), align="C")

        # Descrizione
        pdf.set_xy(x + 5, y + 35)
        pdf.set_font("helvetica", "", 8.5)
        pdf.set_text_color(50, 50, 50)
        testo = str(row['descrizione'])
        if len(testo) > 165: testo = testo[:162] + "..."
        pdf.multi_cell(box_w - 10, 4.2, testo, align="C")

        # Contatti in basso alla card
        pdf.set_xy(x + 6, y + 56)
        pdf.set_font("helvetica", "B", 8)
        pdf.set_text_color(*BLUE_ASSAFRICA)
        pdf.cell(box_w - 12, 4.5, f"Ref: {str(row['referente'])}", ln=True)
        pdf.set_font("helvetica", "", 8)
        pdf.set_x(x + 6)
        pdf.cell(box_w - 12, 4, str(row['email']).lower(), ln=True)
        pdf.set_x(x + 6)
        pdf.set_text_color(*GOLD_ASSAFRICA)
        pdf.cell(box_w - 12, 4, str(row['sito']).lower(), align="L")
        
        i_cat += 1
    
    if not os.path.exists("exports"): os.makedirs("exports")
    final_path = f"exports/{output_name}"
    pdf.output(final_path)
    return final_path

def genera_scheda_socio(socio):
    """One-Pager sincronizzato con il nuovo stile istituzionale"""
    conf = leggi_config()
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    
    # Header a doppia fascia
    pdf.set_fill_color(*BLUE_ASSAFRICA)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_fill_color(*GOLD_ASSAFRICA)
    pdf.rect(0, 40, 210, 2, 'F')
    
    logo_neg = conf.get('logo_negativo', '')
    logo_inst = conf.get('logo_istituzionale', '')
    path_logo_head = logo_neg if (logo_neg and os.path.exists(logo_neg)) else logo_inst
    
    if path_logo_head and os.path.exists(path_logo_head):
        pdf.image(path_logo_head, 12, 8, 25)
    
    pdf.set_xy(42, 15)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, conf.get('nome_associazione', 'ASSAFRICA').upper(), ln=True)
    
    pdf.ln(35)
    
    # Titolo e Settore
    pdf.set_font("helvetica", "B", 26)
    pdf.set_text_color(*BLUE_ASSAFRICA)
    pdf.multi_cell(0, 12, str(socio['nome']).upper(), align="L")
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(*GOLD_ASSAFRICA)
    pdf.cell(0, 10, str(socio['categoria']).upper(), ln=True)
    
    pdf.ln(10)
    
    # Corpo: Logo Azienda + Descrizione
    y_anchor = pdf.get_y()
    if socio['logo_path'] and os.path.exists(socio['logo_path']):
        pdf.image(socio['logo_path'], 15, y_anchor, 50)
        pdf.set_xy(75, y_anchor)
        w_desc = 120
    else:
        pdf.set_x(15)
        w_desc = 180

    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(w_desc, 6, str(socio['descrizione']))
    
    # Box Operatività
    pdf.ln(15)
    pdf.set_fill_color(248, 249, 250)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(*BLUE_ASSAFRICA)
    pdf.cell(0, 10, "  PRESENZA E OPERATIVITÀ IN AFRICA", ln=True, fill=True)
    pdf.set_font("helvetica", "", 10)
    pdf.multi_cell(0, 8, f"  {socio['sede']}", border='B', fill=True)
    
    # Contatti footer
    pdf.set_y(-30)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(*BLUE_ASSAFRICA)
    pdf.cell(0, 6, f"Referente: {socio['referente']}  |  Email: {socio['email']}", ln=True, align="C")
    pdf.set_text_color(*GOLD_ASSAFRICA)
    pdf.cell(0, 6, f"Web: {socio['sito']}", ln=True, align="C")

    safe_name = "".join(x for x in str(socio['nome']) if x.isalnum() or x==' ').replace(' ', '_')
    output_path = f"exports/Scheda_{safe_name}.pdf"
    pdf.output(output_path)
    return output_path