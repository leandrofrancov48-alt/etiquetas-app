import streamlit as st
import fitz  # PyMuPDF
import io

def generar_pdf_grilla_2x2(archivos_subidos):
    if not archivos_subidos:
        return None

    doc_final = fitz.open()
    
    # --- CONFIGURACIÓN A4 VERTICAL (PORTRAIT) ---
    ancho_hoja = 595
    alto_hoja = 842
    
    # Definimos 4 cuadrantes (2 columnas x 2 filas)
    # Mitad del ancho y mitad del alto
    mid_w = ancho_hoja / 2
    mid_h = alto_hoja / 2
    
    # Coordenadas de los 4 espacios [x0, y0, x1, y1]
    # Dejamos 10px de margen interno para que no se peguen
    rects = [
        fitz.Rect(10, 10, mid_w - 5, mid_h - 5),            # 1. Arriba Izq
        fitz.Rect(mid_w + 5, 10, ancho_hoja - 10, mid_h - 5), # 2. Arriba Der
        fitz.Rect(10, mid_h + 5, mid_w - 5, alto_hoja - 10),  # 3. Abajo Izq
        fitz.Rect(mid_w + 5, mid_h + 5, ancho_hoja - 10, alto_hoja - 10) # 4. Abajo Der
    ]
    
    idx_posicion = 0
    page_actual = None

    for archivo_upload in archivos_subidos:
        # Leemos el archivo
        bytes_pdf = archivo_upload.read()
        doc_item = fitz.open(stream=bytes_pdf, filetype="pdf")
        page_source = doc_item[0] 

        # --- RECORTE (CROP) REFINADO ---
        # Ajustamos el recorte para quitar aire y que el contenido
        # se vea lo más grande posible dentro del cuadrante.
        # x1=400 quita el blanco derecho.
        # y1=550 quita un poco de blanco abajo (si la etiqueta es corta).
        crop_box = fitz.Rect(10, 10, 400, 560) 
        page_source.set_cropbox(crop_box)

        # Si es el primer elemento (0) o múltiplo de 4, creamos hoja nueva
        if idx_posicion % 4 == 0:
            page_actual = doc_final.new_page(width=ancho_hoja, height=alto_hoja)
            idx_posicion = 0 # Reseteamos el contador relativo a la página

        # Pegamos en el cuadrante correspondiente
        # keep_proportion=True es CLAVE para que no se deforme
        page_actual.show_pdf_page(rects[idx_posicion], doc_item, 0, keep_proportion=True)
        
        idx_posicion += 1

    # Guardar
    buffer_salida = io.BytesIO()
    doc_final.save(buffer_salida)
    buffer_salida.seek(0)
    return buffer_salida

# --- INTERFAZ ---
st.set_page_config(page_title="Etiquetas 2x2", layout="centered")

st.title("🖨️ Etiquetas: Modo Grilla (4 por hoja)")
st.write("Ideal para ahorrar papel. Sube 1, 2, 3 o 4 etiquetas y salen en una sola A4.")

archivos = st.file_uploader("Seleccioná los PDFs", type="pdf", accept_multiple_files=True)

if archivos:
    if st.button("Procesar Etiquetas"):
        with st.spinner('Acomodando en grilla...'):
            pdf_bytes = generar_pdf_grilla_2x2(archivos)
            
            st.success(f"¡Listo! {len(archivos)} etiquetas procesadas.")
            
            st.download_button(
                label="⬇️ Descargar PDF Final",
                data=pdf_bytes,
                file_name="ETIQUETAS_GRILLA.pdf",
                mime="application/pdf"
            )
