import streamlit as st
import fitz  # PyMuPDF
import io

def generar_pdf_inteligente(archivos_subidos):
    if not archivos_subidos:
        return None

    cantidad = len(archivos_subidos)
    doc_final = fitz.open()
    
    # --- LOGICA DE LAYOUT ---
    # Si son EXACTAMENTE 3, usamos Hoja Horizontal con 3 Columnas.
    # Para cualquier otro caso (1, 2, 4, etc), usamos la Grilla 2x2 Vertical (que se ven más grandes).
    
    es_caso_de_tres = (cantidad == 3)

    if es_caso_de_tres:
        # --- MODO TIRA (3 al hilo) ---
        ancho_hoja = 842 # A4 Landscape
        alto_hoja = 595
        
        # Dividimos el ancho en 3
        ancho_columna = ancho_hoja / 3
        
        # Definimos las 3 posiciones (Izquierda, Medio, Derecha)
        rects = [
            fitz.Rect(10, 20, ancho_columna - 5, alto_hoja - 20),                # 1
            fitz.Rect(ancho_columna + 5, 20, (ancho_columna * 2) - 5, alto_hoja - 20), # 2
            fitz.Rect((ancho_columna * 2) + 5, 20, ancho_hoja - 10, alto_hoja - 20)    # 3
        ]
        # Creamos la hoja una sola vez
        page_actual = doc_final.new_page(width=ancho_hoja, height=alto_hoja)

    else:
        # --- MODO GRILLA 2x2 (Estándar) ---
        ancho_hoja = 595 # A4 Portrait
        alto_hoja = 842
        
        mid_w = ancho_hoja / 2
        mid_h = alto_hoja / 2
        
        rects = [
            fitz.Rect(10, 10, mid_w - 5, mid_h - 5),            # Arr-Izq
            fitz.Rect(mid_w + 5, 10, ancho_hoja - 10, mid_h - 5), # Arr-Der
            fitz.Rect(10, mid_h + 5, mid_w - 5, alto_hoja - 10),  # Abj-Izq
            fitz.Rect(mid_w + 5, mid_h + 5, ancho_hoja - 10, alto_hoja - 10) # Abj-Der
        ]
        # La página se crea dentro del loop según se necesite

    # --- PROCESAMIENTO ---
    idx_posicion = 0
    
    # Si no es caso de 3, necesitamos controlar la creación de páginas en el loop
    page_grid = None 

    for archivo_upload in archivos_subidos:
        bytes_pdf = archivo_upload.read()
        doc_item = fitz.open(stream=bytes_pdf, filetype="pdf")
        page_source = doc_item[0]

        # Recorte estándar (quita bordes blancos)
        crop_box = fitz.Rect(10, 10, 400, 560)
        page_source.set_cropbox(crop_box)

        if es_caso_de_tres:
            # En modo 3, usamos la página única que creamos al principio
            target_page = page_actual
            target_rect = rects[idx_posicion]
        else:
            # En modo Grilla, creamos página cada 4 etiquetas
            if idx_posicion % 4 == 0:
                page_grid = doc_final.new_page(width=ancho_hoja, height=alto_hoja)
                idx_posicion = 0 # Reiniciamos contador por página
            
            target_page = page_grid
            target_rect = rects[idx_posicion]

        # Pegamos
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
* **1, 2 o 4 etiquetas:** Salen en cuadrícula.
* **3 etiquetas:** Salen las 3 en fila.
""")

archivos = st.file_uploader("Subí los archivos aquí", type="pdf", accept_multiple_files=True)

if archivos:
    if st.button("Procesar Etiquetas"):
        with st.spinner('Acomodando según cantidad...'):
            pdf_bytes = generar_pdf_inteligente(archivos)
            
            st.success(f"¡Listo! Procesadas {len(archivos)} etiquetas.")
            
            st.download_button(
                label="⬇️ Descargar PDF Final",
                data=pdf_bytes,
                file_name="ETIQUETAS_LISTAS.pdf",
                mime="application/pdf"
            )

