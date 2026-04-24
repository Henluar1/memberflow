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
    nome_ass = conf.get('nome_associazione', 'CONFINDUSTRIA ASSAFRICA & MEDITERRANEO')

    # --- 1. COVER PAGE (FIX TESTO E BILANCIAMENTO) ---
    pdf.add_page()
    
    # Sfondo: Fascia Blu a sinistra (ridotta leggermente per bilanciare il logo)
    pdf.set_fill_color(*BLUE_ASSAFRICA)
    pdf.rect(0, 0, 95, 210, 'F')
    
    # Linea Oro di accento verticale
    pdf.set_fill_color(*GOLD_ASSAFRICA)
    pdf.rect(95, 0, 2.5, 210, 'F')
    
    # Logo Grande centrato nella sezione bianca (Usa logo standard colorato)
    if logo_inst and os.path.exists(logo_inst):
        w_logo = 95
        x_logo = 97.5 + (297 - 97.5 - w_logo) / 2
        pdf.image(logo_inst, x=x_logo, y=75, w=w_logo) 
    
    # Titoli sulla fascia Blu
    pdf.set_text_color(255, 255, 255)
    
    # BUSINESS COMMUNITY - Ridotto a 32pt per evitare rotture "Communit-y"
    pdf.set_xy(10, 85)
    pdf.set_font("helvetica", "B", 32)
    pdf.multi_cell(80, 12, "BUSINESS\nCOMMUNITY", align="L")
    
    # 2026 - Posizionato con spazio corretto sotto
    pdf.set_xy(10, 112)
    pdf.set_font("helvetica", "", 28)
    pdf.cell(80, 15, "2026", ln=True, align="L")
    
    # Nome Associazione in basso
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
        pdf.cell(0, 10, f"{current_cat.upper()} / {page_in_cat}", ln=True)

        pos_in_page = i_cat % 6
        col, fila = pos_in_page % 3, pos_in_page // 3
        x, y = margin_x + (col * (box_w + 6)), margin_y_start + (fila * (box_h + 8))
        
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(230, 230, 230)
        pdf.set_line_width(0.2)
        pdf.rect(x, y, box_w, box_h, 'DF')
        
        if row['logo_path'] and os.path.exists(row['logo_path']):
            pdf.image(row['logo_path'], x=x + (box_w-45)/2, y=y + 6, w=45)
        else:
            pdf.set_xy(x + 5, y + 15)
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(*BLUE_ASSAFRICA)
            pdf.multi_cell(box_w - 10, 5, str(row['nome']).upper(), align="C")

        pdf.set_xy(x + 5, y + 35)
        pdf.set_font("helvetica", "", 8.5)
        pdf.set_text_color(50, 50, 50)
        testo = str(row['descrizione'])
        if len(testo) > 165: testo = testo[:162] + "..."
        pdf.multi_cell(box_w - 10, 4.2, testo, align="C")

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

# --- ONE PAGER (DESIGN SINCRONIZZATO E FIX LAYOUT) ---
def genera_scheda_socio(socio):
    conf = leggi_config()
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False) # Evita che salti a pagina 2 per piccoli sforamenti
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    
    # Header istituzionale
    pdf.set_fill_color(*BLUE_ASSAFRICA)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_fill_color(*GOLD_ASSAFRICA)
    pdf.rect(0, 40, 210, 2, 'F')
    
    logo_neg = conf.get('logo_negativo', '')
    logo_std = conf.get('logo_istituzionale', '')
    path_logo_head = logo_neg if (logo_neg and os.path.exists(logo_neg)) else logo_std
    
    if path_logo_head and os.path.exists(path_logo_head):
        pdf.image(path_logo_head, 12, 8, 25)
    
    pdf.set_xy(42, 16)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, conf.get('nome_associazione', 'ASSAFRICA').upper(), ln=True)
    
    # Titolo e Settore
    pdf.set_xy(15, 55)
    pdf.set_font("helvetica", "B", 26)
    pdf.set_text_color(*BLUE_ASSAFRICA)
    pdf.multi_cell(180, 12, str(socio['nome']).upper(), align="L")
    
    pdf.set_x(15)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(*GOLD_ASSAFRICA)
    pdf.cell(0, 10, str(socio['categoria']).upper(), ln=True)
    
    # Corpo: Logo Azienda + Descrizione
    pdf.ln(5)
    y_anchor = pdf.get_y()
    if socio['logo_path'] and os.path.exists(socio['logo_path']):
        pdf.image(socio['logo_path'], 15, y_anchor, 50)
        pdf.set_xy(75, y_anchor)
        w_desc = 120
    else:
        pdf.set_x(15)
        w_desc = 180

    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    # Multi_cell con altezza controllata per non sforare
    pdf.multi_cell(w_desc, 7, str(socio['descrizione']))
    
    # Box Operatività
    pdf.set_y(max(pdf.get_y() + 10, 130)) # Garantisce spazio anche con descrizioni brevi
    pdf.set_fill_color(248, 249, 250)
    pdf.set_draw_color(230, 230, 230)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(*BLUE_ASSAFRICA)
    pdf.cell(180, 10, "  PRESENZA E OPERATIVITÀ IN AFRICA", ln=True, fill=True, border='T')
    
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    paesi = str(socio['sede']) if socio['sede'] else "N/A"
    pdf.multi_cell(180, 8, f"  {paesi}", fill=True, border='B')
    
    # Contatti footer (Ancorati in basso)
    pdf.set_y(250)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(*BLUE_ASSAFRICA)
    pdf.cell(0, 6, f"Referente: {socio['referente']}  |  Email: {socio['email']}", ln=True, align="C")
    pdf.set_text_color(*GOLD_ASSAFRICA)
    pdf.cell(0, 6, f"Sito Web: {socio['sito']}", ln=True, align="C")

    # Footer Istituzionale
    pdf.set_y(280)
    pdf.set_font("helvetica", "I", 7)
    pdf.set_text_color(150, 150, 150)
    info_conf = f"{conf.get('indirizzo', '')} | {conf.get('email_contatto', '')}"
    pdf.cell(0, 10, f"{info_conf} - Generato il {datetime.now().strftime('%d/%m/%Y')}", 0, 0, "C")

    safe_name = "".join(x for x in str(socio['nome']) if x.isalnum() or x==' ').replace(' ', '_').upper()
    output_path = f"exports/Scheda_{safe_name}.pdf"
    pdf.output(output_path)
    return output_path
