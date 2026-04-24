from fpdf import FPDF
import os
from modules.database_manager import leggi_config

class CatalogoPDF(FPDF):
    def header(self):
        # Header minimale: Logo istituzionale in alto a destra se esiste
        conf = leggi_config()
        logo_inst = conf.get('logo_istituzionale', '')
        
        if logo_inst and os.path.exists(logo_inst):
            self.image(logo_inst, 260, 8, 22) # Posizionato in alto a dx
            
    def footer(self):
        # Piè di pagina in stile originale "- Numero -"
        self.set_y(-12)
        self.set_font("helvetica", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"- {self.page_no()} -", align="C")
        
def genera_catalogo(df_soci, output_name="Catalogo_Associati_2026.pdf"):
    pdf = CatalogoPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    df_soci = df_soci.sort_values(by=['categoria', 'nome'])
    categorie = df_soci['categoria'].unique()
    
    # --- 1. INDICE ---
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(0, 45, 90)
    pdf.cell(0, 20, "INDICE", ln=True, align="L")
    pdf.ln(5)
    
    links = {}
    current_p = 2 # Pagina 1 è l'indice, i dati iniziano a pag 2
    for cat in categorie:
        links[cat] = pdf.add_link()
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.write(8, cat.upper(), link=links[cat])
        
        # Punti di riempimento per l'indice
        x_curr = pdf.get_x() + 3
        pdf.set_draw_color(220, 220, 220)
        for i in range(int(x_curr), 275, 4):
            pdf.line(i, pdf.get_y() + 5, i + 1, pdf.get_y() + 5)
            
        pdf.set_x(277)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(10, 8, str(current_p), align="R", ln=True)
        
        # Calcolo pagine occupate da questa categoria (6 schede per pagina)
        num_soci = len(df_soci[df_soci['categoria'] == cat])
        current_p += (num_soci + 5) // 6

    # --- 2. SCHEDE (Griglia 3x2 come originale) ---
    current_cat = None
    page_in_cat = 1
    
    # Dimensioni calcolate per A4 Orizzontale (297x210)
    box_w, box_h = 85, 76
    margin_x, margin_y_start = 15, 30
    spacing_x, spacing_y = 6, 8

    for i, (_, row) in enumerate(df_soci.iterrows()):
        # Nuova Categoria
        if row['categoria'] != current_cat:
            current_cat = row['categoria']
            page_in_cat = 1
            i_cat = 0
            
            pdf.add_page()
            pdf.set_link(links[current_cat])
            
            # Intestazione Categoria in alto a sinistra (es. AGROALIMENTARE / 1)
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(100, 100, 100)
            pdf.set_xy(15, 15)
            pdf.cell(0, 10, f"{current_cat.upper()} / {page_in_cat}", ln=True)
        
        # Gestione Nuova Pagina all'interno della stessa categoria
        pos_in_page = i_cat % 6
        if pos_in_page == 0 and i_cat > 0:
            pdf.add_page()
            page_in_cat += 1
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(100, 100, 100)
            pdf.set_xy(15, 15)
            pdf.cell(0, 10, f"{current_cat.upper()} / {page_in_cat}", ln=True)

        col = pos_in_page % 3
        fila = pos_in_page // 3
        
        x = margin_x + (col * (box_w + spacing_x))
        y = margin_y_start + (fila * (box_h + spacing_y))
        
        # Disegno la Card (Bordo grigio spesso, niente riempimento)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(225, 225, 225) # Grigio chiaro
        pdf.set_line_width(1.5) # Bordo spesso
        pdf.rect(x, y, box_w, box_h, 'DF')
        
        # --- LOGO CENTRATO IN ALTO ---
        if row['logo_path'] and os.path.exists(row['logo_path']):
            w_max = 45 # Larghezza fissa ragionevole per loghi
            x_logo = x + (box_w - w_max) / 2
            pdf.image(row['logo_path'], x=x_logo, y=y + 5, w=w_max)
        else:
            pdf.set_xy(x + 2, y + 15)
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(0, 45, 90)
            pdf.multi_cell(box_w - 4, 5, str(row['nome']).upper(), align="C")

        # --- DESCRIZIONE CENTRATA ---
        pdf.set_xy(x + 5, y + 32) # Ancoraggio fisso al centro della card
        pdf.set_font("helvetica", "", 8.5)
        pdf.set_text_color(40, 40, 40)
        testo = str(row['descrizione'])
        if len(testo) > 160: testo = testo[:157] + "..."
        pdf.multi_cell(box_w - 10, 4, testo, align="C")

        # --- CONTATTI ALLINEATI A SINISTRA (In Basso) ---
        pdf.set_xy(x + 6, y + 56) # Ancoraggio fisso in basso
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(box_w - 12, 4.5, f"Referente A&M: {str(row['referente'])}", ln=True, align="L")
        
        pdf.set_x(x + 6)
        pdf.cell(box_w - 12, 4.5, str(row['email']).lower(), ln=True, align="L")
        
        pdf.set_x(x + 6)
        pdf.cell(box_w - 12, 4.5, str(row['sito']).lower(), align="L")
        
        i_cat += 1
    
    pdf.output(output_name)
    return output_name