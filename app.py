import streamlit as st
import fitz  # PyMuPDF
import io

def generar_pdf_inteligente(archivos_subidos):
    if not archivos_subidos:
        return None

    cantidad = len(archivos_subidos)
    doc_final = fitz.open()
    
    # Determinamos si es el caso especial de "Tira de 3"
    es_caso_de_tres = (cantidad == 3)

    if es_caso_de_tres:
        # --- MODO TIRA (3 al hilo - ESTILO NATTO) ---
        ancho_hoja = 842 # A4 Landscape
        alto_hoja = 595
        
        # Dividimos el ancho en 3 partes EXACTAS sin perder espacio
        ancho_columna = ancho_hoja / 3
        
        # Definimos las 3 posiciones SIN márgenes internos
        # Usamos todo el ancho disponible.
        # Rect(x0, y0, x1, y1)
        rects = [
            fitz.Rect(0, 10, ancho_columna, alto_hoja - 10),                # 1. Izquierda
            fitz.Rect(ancho_columna, 10, ancho_columna * 2, alto_hoja - 10), # 2. Medio
            fitz.Rect(ancho_columna * 2, 10, ancho_hoja, alto_hoja - 10)     # 3. Derecha
        ]
        
        page_actual = doc_final.new_page(width=ancho_hoja, height=alto_hoja)

    else:
        # --- MODO GRILLA 2x2 (Estándar para 1, 2 o 4) ---
        ancho_hoja = 595 # A4 Portrait
        alto_hoja = 842
        
        mid_w = ancho_hoja / 2
        mid_h = alto_hoja / 2
        
        rects = [
            fitz.Rect(5, 5, mid_w, mid_h),              # Arr-Izq
            fitz.Rect(mid_w, 5, ancho_hoja - 5, mid_h), # Arr-Der
            fitz.Rect(5, mid_h, mid_w, alto_hoja - 5),  # Abj-Izq
            fitz.Rect(mid_w, mid_h, ancho_hoja - 5, alto_hoja - 5) # Abj-Der
        ]
        page_grid = None 

    # --- PROCESAMIENTO ---
    idx_posicion = 0
    
    for archivo_upload in archivos_subidos:
        bytes_pdf = archivo_upload.read()
        doc_item = fitz.open(stream=bytes_pdf, filetype="pdf")
        page_source = doc_item[0]

        # --- RECORTE (CROP) MÁS AGRESIVO ---
        # Antes x1 era 400. Lo bajamos a 385 para eliminar el blanco derecho.
        # Esto hace que la etiqueta se vea "más grande" al pegarse.
        crop_box = fitz.Rect(5, 10, 385, 560)
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

        # Pegamos la etiqueta
        target_page.show_pdf_page(target_rect, doc_item, 0, keep_proportion=True)
        
        idx_posicion += 1

    # Guardar
    buffer_salida = io.BytesIO()
    doc_final.save(buffer_salida)
    buffer_salida.seek(0)
    return buffer_salida

# --- INTERFAZ ---
st.set_page_config(page_title="Etiquetas Inteligentes", layout="centered")

st.title("🖨️ Etiquetas PDF")
st.markdown("""
* **3 etiquetas:** Salen pegadas en fila horizontal (Estilo compacto).
* **1, 2 o 4 etiquetas:** Salen en cuadrícula vertical.
""")

archivos = st.file_uploader("Subí los archivos aquí", type="pdf", accept_multiple_files=True)

if archivos:
    if st.button("Procesar Etiquetas"):
        with st.spinner('Procesando...'):
            pdf_bytes = generar_pdf_inteligente(archivos)
            st.success(f"¡Listo! {len(archivos)} etiquetas procesadas.")
            st.download_button(
                label="⬇️ Descargar PDF Final",
                data=pdf_bytes,
                file_name="ETIQUETAS_LISTAS.pdf",
                mime="application/pdf"
            )
