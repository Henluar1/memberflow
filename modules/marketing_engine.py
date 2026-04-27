from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# Colori Istituzionali Assafrica
BLUE_ASSAFRICA = (0, 45, 90)
GOLD_ASSAFRICA = (184, 151, 93)
WHITE = (255, 255, 255)
DARK_GRAY = (100, 100, 100) 
SHADOW_COLOR = (0, 10, 20) # Blu scurissimo per ombra profonda e realistica

def _get_font(size):
    font_paths = [
        "arial.ttf", "/Library/Fonts/Arial.ttf", 
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except IOError:
            continue
    return ImageFont.load_default()

def incolla_loghi_multipli(img, draw, paths, max_w, max_h, start_x, start_y, spacing=40, align="left", divisori=False):
    """Incolla loghi multipli mantenendo proporzioni e disegnando linee divisorie opzionali"""
    if not paths: return 0, 0 
    
    valid_paths = [p for p in paths if p and os.path.exists(p)]
    images = []
    
    for p in valid_paths:
        try:
            l = Image.open(p).convert("RGBA")
            l.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            images.append(l)
        except Exception as e:
            print(f"Errore logo {p}:", e)

    if not images: return 0, 0

    total_w = sum(img_obj.width for img_obj in images) + spacing * (len(images) - 1)
    max_img_h = max(img_obj.height for img_obj in images)
    
    current_x = start_x
    if align == "right":
        current_x = start_x - total_w

    for i, img_obj in enumerate(images):
        offset_y = start_y + (max_h - img_obj.height) // 2
        img.paste(img_obj, (current_x, offset_y), img_obj)
        
        # DISEGNO LINEA DIVISORIA ELEGANTE SE RICHIESTA
        if divisori and i < len(images) - 1:
            line_x = current_x + img_obj.width + (spacing // 2)
            line_y1 = start_y + int(max_h * 0.15)
            line_y2 = start_y + int(max_h * 0.85)
            draw.line([(line_x, line_y1), (line_x, line_y2)], fill=(210, 210, 210), width=2)
            
        current_x += img_obj.width + spacing
        
    return total_w, max_img_h

def genera_banner(titolo, sottotitolo, data_luogo, tipo="linkedin", logo_inst=None, loghi_org=None, loghi_partner=None, sfondo_dx=None):
    if loghi_org is None: loghi_org = []
    if loghi_partner is None: loghi_partner = []

    # 1. Impostazione Dimensioni Dinamiche e Spaziature per Formato
    if tipo == "linkedin":
        width, height = 1200, 627
        h_top, h_bot = 100, 110
        wrap_t, wrap_s = 30, 55
        margin_left = 60
        f_tit, f_sot, f_dat, f_lab = 65, 32, 28, 14
        logo_part_w, logo_part_h = 220, 50
    else: # instagram quadrato
        width, height = 1080, 1080
        h_top, h_bot = 130, 180 # Più spazio in basso per respirare
        wrap_t, wrap_s = 16, 35 # Forza a-capo anticipato per evitare tagli laterali
        margin_left = 70
        f_tit, f_sot, f_dat, f_lab = 60, 34, 30, 16
        logo_part_w, logo_part_h = 180, 60
        
    img = Image.new('RGB', (width, height), color=WHITE)
    draw = ImageDraw.Draw(img)
    
    # 2. Fascia Blu e Linea Oro
    draw.rectangle([(0, h_top), (width, height - h_bot)], fill=BLUE_ASSAFRICA)
    draw.rectangle([(0, height - h_bot), (width, height - h_bot + 4)], fill=GOLD_ASSAFRICA)

    # 3. Sfondo con SFUMATURA Adattiva
    if sfondo_dx and os.path.exists(sfondo_dx):
        try:
            bg = Image.open(sfondo_dx).convert("RGBA")
            target_h = height - h_top - h_bot
            ratio = target_h / float(bg.height)
            new_w = int(float(bg.width) * ratio)
            bg = bg.resize((new_w, target_h), Image.Resampling.LANCZOS)
            
            pixels = bg.load()
            # La sfumatura prende il 45% su Linkedin, ma il 60% su Instagram per salvare il testo
            fade_percent = 0.6 if tipo == "instagram" else 0.45
            fade_width = int(bg.width * fade_percent) 
            
            for y in range(bg.height):
                for x in range(bg.width):
                    if x < fade_width:
                        r, g, b, a = pixels[x, y]
                        new_a = int(a * (x / fade_width))
                        pixels[x, y] = (r, g, b, new_a)
            
            pos_x = width - new_w
            img.paste(bg, (pos_x, h_top), bg)
        except Exception as e:
            print("Errore sfondo:", e)

    # 4. Font
    font_titolo = _get_font(f_tit)
    font_sotto = _get_font(f_sot)
    font_data = _get_font(f_dat)
    font_labels = _get_font(f_lab)
    
    # 5. Testi con OMBRA 3D PROFONDA
    y_text = h_top + (50 if tipo == "linkedin" else 70)
    wrapped_titolo = textwrap.fill(titolo.upper(), width=wrap_t)
    
    # Livello 1: Ombra Esterna (Soft)
    draw.multiline_text((margin_left + 4, y_text + 4), wrapped_titolo, fill=SHADOW_COLOR, font=font_titolo, spacing=16)
    # Livello 2: Ombra Interna (Hard)
    draw.multiline_text((margin_left + 2, y_text + 2), wrapped_titolo, fill=SHADOW_COLOR, font=font_titolo, spacing=16)
    # Livello 3: Testo Bianco Base
    draw.multiline_text((margin_left, y_text), wrapped_titolo, fill=WHITE, font=font_titolo, spacing=16)
    
    try:
        bbox = draw.multiline_textbbox((margin_left, y_text), wrapped_titolo, font=font_titolo, spacing=16)
        y_text = bbox[3] + 35 
    except:
        y_text += 180
        
    wrapped_sotto = textwrap.fill(sottotitolo, width=wrap_s)
    # Ombra e testo per Sottotitolo
    draw.multiline_text((margin_left + 2, y_text + 2), wrapped_sotto, fill=SHADOW_COLOR, font=font_sotto, spacing=8)
    draw.multiline_text((margin_left, y_text), wrapped_sotto, fill=GOLD_ASSAFRICA, font=font_sotto, spacing=8)
    
    y_data = height - h_bot - 45 if tipo=="linkedin" else height - h_bot - 65
    # Ombra e testo per Data/Luogo
    draw.text((margin_left + 2, y_data + 2), data_luogo.upper(), fill=SHADOW_COLOR, font=font_data)
    draw.text((margin_left, y_data), data_luogo.upper(), fill=WHITE, font=font_data)
    
    # 6. Loghi Fascia Alta (Header)
    incolla_loghi_multipli(img, draw, [logo_inst], 300, h_top - 30, margin_left, 15, align="left")
    
    if loghi_org:
        # Passiamo divisori=True per le lineette
        w_org, h_org = incolla_loghi_multipli(img, draw, loghi_org, 180, h_top - 40, width - margin_left, 25, spacing=40, align="right", divisori=True)
        x_label_org = width - margin_left - w_org
        draw.text((x_label_org, 8), "Organized by:", fill=DARK_GRAY, font=font_labels)

    # 7. Loghi Fascia Bassa (Footer)
    if loghi_partner:
        draw.text((margin_left, height - h_bot + 15), "Official Partners / Supported by:", fill=DARK_GRAY, font=font_labels)
        # Passiamo divisori=True per le lineette
        incolla_loghi_multipli(img, draw, loghi_partner, logo_part_w, logo_part_h, margin_left, height - h_bot + 45, spacing=40, align="left", divisori=True)

    # 8. Export
    if not os.path.exists("exports"): os.makedirs("exports")
    output_path = f"exports/banner_{tipo}.jpg"
    img = img.convert("RGB")
    img.save(output_path, quality=95)
    
    return output_path