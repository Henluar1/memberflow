from fpdf import FPDF
import os
from modules.database_manager import leggi_config # <--- Recuperiamo i dati di Assafrica

class CatalogoPDF(FPDF):
    def header(self):
        conf = leggi_config()
        logo_inst = conf.get('logo_istituzionale', '')
        nome_ass = conf.get('nome_associazione', 'Associazione')

        # Se esiste il logo istituzionale, lo mettiamo a sinistra
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
        self.ln(15)

    def footer(self):
        conf = leggi_config()
        indirizzo = conf.get('indirizzo', '')
        email = conf.get('email_contatto', '')
        
        self.set_y(-15)
        self.set_font("helvetica", "I", 7)
        self.set_text_color(120)
        # Piè di pagina con i contatti inseriti in Configurazione
        info_footer = f"{indirizzo} | {email}" if indirizzo else "Documento Istituzionale"
        self.cell(0, 10, f"{info_footer} - Pagina {self.page_no()}", align="C")
        
def genera_catalogo(df_soci, output_name="Catalogo_Orizzontale.pdf"):
    # Inizializzazione PDF Orizzontale
    pdf = CatalogoPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Ordinamento per categoria e nome
    df_soci = df_soci.sort_values(by=['categoria', 'nome'])
    categorie = df_soci['categoria'].unique()
    
    # --- 1. PAGINA INDICE ---
    pdf.add_page()
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(0, 45, 90)
    pdf.cell(0, 20, "INDICE", ln=True, align="C")
    pdf.ln(10)
    
    links = {}
    current_p = 2 # I contenuti iniziano dopo l'indice
    pdf.set_font("helvetica", "", 11)
    
    for cat in categorie:
        links[cat] = pdf.add_link()
        pdf.set_text_color(0, 45, 90)
        
        # Scriviamo la categoria
        nome_cat = cat.upper()
        pdf.write(10, nome_cat, link=links[cat])
        
        # DISEGNO LINEA TRATTEGGIATA (Leader Lines)
        x_start = pdf.get_x() + 3
        pdf.set_draw_color(180) # Grigio per i puntini
        pdf.set_line_width(0.3)
        # Disegniamo trattini ogni 3mm fino al margine destro (270mm)
        for i in range(int(x_start), 270, 3):
            pdf.line(i, pdf.get_y() + 7, i + 1, pdf.get_y() + 7)
            
        # Numero di pagina a destra
        pdf.set_x(272)
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(15, 10, str(current_p), align="R", ln=True)
        
        # Calcolo dinamico: 8 soci per pagina (2 righe da 4)
        num_soci = len(df_soci[df_soci['categoria'] == cat])
        pagine_occupate = (num_soci + 7) // 8
        current_p += pagine_occupate
        
        # Ripristiniamo font per la riga successiva
        pdf.set_font("helvetica", "", 11)

    # --- 2. SCHEDE ASSOCIATI ---
    current_cat = None
    col_w, row_h, margin_x, spacing = 65, 80, 15, 5

    for _, row in df_soci.iterrows():
        # Se cambia la categoria, creiamo una nuova pagina con testata
        if row['categoria'] != current_cat:
            current_cat = row['categoria']
            pdf.add_page()
            pdf.set_link(links[current_cat])
            
            pdf.set_font("helvetica", "B", 18)
            pdf.set_text_color(0, 45, 90)
            pdf.cell(0, 12, current_cat.upper(), ln=True)
            
            # Linea Oro di separazione
            pdf.set_draw_color(184, 151, 93) 
            pdf.set_line_width(0.8)
            pdf.line(15, pdf.get_y(), 282, pdf.get_y())
            pdf.ln(10)
            i_cat = 0
        
        # Posizionamento nella griglia 4x2
        col = i_cat % 4
        if col == 0 and i_cat > 0:
            pdf.ln(row_h + spacing)
            if pdf.get_y() > 160: # Margine di sicurezza per landscape
                pdf.add_page()
        
        x, y = margin_x + (col * (col_w + spacing)), pdf.get_y()
        
        # Box del socio
        pdf.set_draw_color(220)
        pdf.set_line_width(0.2)
        pdf.rect(x, y, col_w, row_h)
        
        # Logo o Nome
        if row['logo_path'] and os.path.exists(row['logo_path']):
            # Adattamento logo centrato
            pdf.image(row['logo_path'], x + (col_w-30)/2, y + 5, 30)
        else:
            pdf.set_xy(x + 2, y + 15)
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(0, 45, 90)
            pdf.multi_cell(col_w - 4, 5, str(row['nome']).upper(), align="C")
        
        # Descrizione attività
        pdf.set_xy(x + 5, y + 38)
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(50)
        testo_desc = str(row['descrizione'])
        if len(testo_desc) > 165: testo_desc = testo_desc[:162] + "..."
        pdf.multi_cell(col_w - 10, 3.8, testo_desc, align="C")
        
        # Contatti a fondo box
        pdf.set_xy(x + 2, y + row_h - 15)
        pdf.set_font("helvetica", "B", 7.5)
        pdf.set_text_color(0)
        pdf.cell(col_w - 4, 4, f"Ref: {row['referente']}", ln=True, align="C")
        pdf.set_font("helvetica", "", 7)
        pdf.set_x(x + 2)
        pdf.cell(col_w - 4, 3.5, str(row['email']).lower(), ln=True, align="C")
        pdf.set_x(x + 2)
        pdf.cell(col_w - 4, 3.5, str(row['sito']).lower(), align="C")
        
        i_cat += 1
    
    pdf.output(output_name)
    return output_name