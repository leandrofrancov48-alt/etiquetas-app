import streamlit as st
import fitz  # PyMuPDF
import io

def generar_pdf_inteligente(archivos_subidos):
    if not archivos_subidos:
        return None

    cantidad = len(archivos_subidos)
    doc_final = fitz.open()
    
    es_caso_de_tres = (cantidad == 3)

    if es_caso_de_tres:
        # --- MODO TIRA (3 PEGADAS) ---
        ancho_hoja = 842 # A4 Horizontal
        alto_hoja = 595
        
        # Dividimos en 3 columnas exactas
        ancho_columna = ancho_hoja / 3
        
        # Rectángulos que ocupan TODO el espacio (sin márgenes entre ellos)
        rects = [
            fitz.Rect(0, 10, ancho_columna, alto_hoja - 10),                 # 1
            fitz.Rect(ancho_columna, 10, ancho_columna * 2, alto_hoja - 10), # 2
            fitz.Rect(ancho_columna * 2, 10, ancho_hoja, alto_hoja - 10)     # 3
        ]
        
        page_actual = doc_final.new_page(width=ancho_hoja, height=alto_hoja)

    else:
        # --- MODO GRILLA 2x2 (Estándar) ---
        ancho_hoja = 595 
        alto_hoja = 842
        
        mid_w = ancho_hoja / 2
        mid_h = alto_hoja / 2
        
        rects = [
            fitz.Rect(0, 0, mid_w, mid_h),              # Arr-Izq
            fitz.Rect(mid_w, 0, ancho_hoja, mid_h),     # Arr-Der
            fitz.Rect(0, mid_h, mid_w, alto_hoja),      # Abj-Izq
            fitz.Rect(mid_w, mid_h, ancho_hoja, alto_hoja) # Abj-Der
        ]
        page_grid = None 

    idx_posicion = 0
    
    for archivo_upload in archivos_subidos:
        bytes_pdf = archivo_upload.read()
        doc_item = fitz.open(stream=bytes_pdf, filetype="pdf")
        page_source = doc_item[0]

        # --- CORTE QUIRÚRGICO ---
        # x0=5: Borde izquierdo casi al ras.
        # x1=315: Borde derecho MUY ajustado (antes 385 o 400).
        # Esto elimina el "aire" y obliga a la etiqueta a verse gigante.
        crop_box = fitz.Rect(5, 10, 315, 580)
        page_source.set_cropbox(crop_box)

        if es_caso_de_tres:
            target_page = page_actual
            target_rect = rects[idx_posicion]
        else:
            if idx_posicion % 4 == 0:
                page_grid = doc_final.new_page(width=ancho_hoja, height=alto_hoja)
                idx_posicion = 0 
            target_page = page_grid
            target_rect = rects[idx_posicion]

        # keep_proportion=True hace que crezca hasta tocar los bordes nuevos
        target_page.show_pdf_page(target_rect, doc_item, 0, keep_proportion=True)
        
        idx_posicion += 1

    buffer_salida = io.BytesIO()
    doc_final.save(buffer_salida)
    buffer_salida.seek(0)
    return buffer_salida

# --- INTERFAZ ---
st.set_page_config(page_title="Etiquetas Ajustadas", layout="centered")

st.title("🖨️ Etiquetas al Máximo")
st.write("Modo optimizado: Recorte agresivo para eliminar espacios blancos.")

archivos = st.file_uploader("Subí los archivos PDF", type="pdf", accept_multiple_files=True)

if archivos:
    if st.button("Procesar Etiquetas"):
        with st.spinner('Ajustando tamaños...'):
            pdf_bytes = generar_pdf_inteligente(archivos)
            st.success(f"¡Listo! {len(archivos)} etiquetas procesadas.")
            st.download_button(
                label="⬇️ Descargar PDF Final",
                data=pdf_bytes,
                file_name="ETIQUETAS_FULL.pdf",
                mime="application/pdf"
            )
