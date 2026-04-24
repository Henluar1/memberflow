from fpdf import FPDF
import os
from modules.database_manager import leggi_config

class CatalogoPDF(FPDF):
    def header(self):
        conf = leggi_config()
        logo_inst = conf.get('logo_istituzionale', '')
        nome_ass = conf.get('nome_associazione', 'Associazione')

        if logo_inst and os.path.exists(logo_inst):
            self.image(logo_inst, 10, 8, 25)
            self.set_x(40)
        else:
            self.set_x(10)

        self.set_font("helvetica", "B", 12)
        self.set_text_color(0, 45, 90)
        self.cell(0, 10, nome_ass.upper(), ln=False, align="L")
        
        self.set_font("helvetica", "B", 8)
        self.set_text_color(150)
        self.cell(0, 10, "CATALOGO UFFICIALE 2026", ln=True, align="R")
        self.ln(10)

    def footer(self):
        conf = leggi_config()
        indirizzo = conf.get('indirizzo', '')
        email = conf.get('email_contatto', '')
        
        self.set_y(-15)
        self.set_font("helvetica", "I", 7)
        self.set_text_color(120)
        info_footer = f"{indirizzo} | {email}" if indirizzo else "Documento Istituzionale"
        self.cell(0, 10, f"{info_footer} - Pagina {self.page_no()}", align="C")
        
def genera_catalogo(df_soci, output_name="Catalogo_Associati_2026.pdf"):
    # Setup Orizzontale (Landscape)
    pdf = CatalogoPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    df_soci = df_soci.sort_values(by=['categoria', 'nome'])
    categorie = df_soci['categoria'].unique()
    
    # --- 1. INDICE ---
    pdf.add_page()
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(0, 45, 90)
    pdf.cell(0, 20, "INDICE", ln=True, align="C")
    pdf.ln(10)
    
    links = {}
    current_p = 2
    for cat in categorie:
        links[cat] = pdf.add_link()
        pdf.set_font("helvetica", "", 11)
        pdf.set_text_color(0, 45, 90)
        pdf.write(10, cat.upper(), link=links[cat])
        
        # Leader lines
        x_curr = pdf.get_x() + 3
        pdf.set_draw_color(200)
        for i in range(int(x_curr), 270, 3):
            pdf.line(i, pdf.get_y() + 7, i + 1, pdf.get_y() + 7)
            
        pdf.set_x(272)
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(15, 10, str(current_p), align="R", ln=True)
        
        num_soci = len(df_soci[df_soci['categoria'] == cat])
        current_p += (num_soci + 7) // 8

    # --- 2. SCHEDE (Griglia 4x2) ---
    current_cat = None
    # Dimensioni box fisse
    box_w, box_h = 66, 82
    margin_x, margin_y_start = 15, 45
    spacing_x, spacing_y = 4, 4

    for _, row in df_soci.iterrows():
        if row['categoria'] != current_cat:
            current_cat = row['categoria']
            pdf.add_page()
            pdf.set_link(links[current_cat])
            
            pdf.set_font("helvetica", "B", 18)
            pdf.set_text_color(0, 45, 90)
            pdf.cell(0, 10, current_cat.upper(), ln=True)
            
            # Linea oro sotto il titolo categoria
            pdf.set_draw_color(184, 151, 93)
            pdf.set_line_width(0.8)
            pdf.line(15, 38, 282, 38)
            i_cat = 0
        
        # Calcolo posizione X e Y
        # i_cat % 8 determina la posizione nella pagina (0-7)
        pos_in_page = i_cat % 8
        if pos_in_page == 0 and i_cat > 0:
            pdf.add_page()
            # Ripetiamo il titolo categoria sulle pagine successive
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(150)
            pdf.cell(0, 10, f"{current_cat.upper()} (segue)", ln=True)
            pdf.ln(5)

        col = pos_in_page % 4
        fila = pos_in_page // 4
        
        x = margin_x + (col * (box_w + spacing_x))
        y = margin_y_start + (fila * (box_h + spacing_y))
        
        # DISEGNO BOX (sfondo leggero per staccare le schede)
        pdf.set_fill_color(252, 252, 252)
        pdf.set_draw_color(220)
        pdf.set_line_width(0.1)
        pdf.rect(x, y, box_w, box_h, 'FD')
        
        # LOGO O TITOLO (Ancoraggio Y + 5)
        if row['logo_path'] and os.path.exists(row['logo_path']):
            # Image(path, x, y, w, h) -> h=0 mantiene proporzioni
            pdf.image(row['logo_path'], x + (box_w-35)/2, y + 5, 35)
        else:
            pdf.set_xy(x + 2, y + 10)
            pdf.set_font("helvetica", "B", 9)
            pdf.set_text_color(0, 45, 90)
            pdf.multi_cell(box_w - 4, 4, str(row['nome']).upper(), align="C")

        # DESCRIZIONE (Ancoraggio Y + 35 fiso)
        pdf.set_xy(x + 4, y + 35)
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(60)
        testo = str(row['descrizione'])
        # Limite caratteri rigoroso per non rompere il layout
        if len(testo) > 180: testo = testo[:177] + "..."
        # multi_cell(w, h, txt)
        pdf.multi_cell(box_w - 8, 3.5, testo, align="C")

        # CONTATTI (Ancoraggio al fondo del box Y + 65)
        # Usiamo set_xy per forzare la posizione indipendentemente dalla descrizione
        pdf.set_xy(x + 2, y + 65)
        pdf.set_font("helvetica", "B", 7)
        pdf.set_text_color(0, 45, 90)
        pdf.cell(box_w - 4, 4, f"REF: {str(row['referente']).upper()}", ln=True, align="C")
        
        pdf.set_font("helvetica", "", 7)
        pdf.set_text_color(100)
        pdf.set_x(x + 2)
        pdf.cell(box_w - 4, 3.5, str(row['email']).lower(), ln=True, align="C")
        pdf.set_x(x + 2)
        pdf.set_text_color(0, 74, 153) # Blu per il link
        pdf.cell(box_w - 4, 3.5, str(row['sito']).lower(), align="C")
        
        i_cat += 1
    
    pdf.output(output_name)
    return output_name