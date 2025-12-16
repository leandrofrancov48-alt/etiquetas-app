import streamlit as st
import fitz  # PyMuPDF
import io

def generar_pdf_lado_a_lado(archivos_subidos):
    if not archivos_subidos:
        return None

    # Creamos el documento final en memoria
    doc_final = fitz.open()
    
    # Medidas A4 Horizontal (Landscape)
    ancho_hoja = 842
    alto_hoja = 595
    
    # Definimos las zonas izquierda y derecha
    rect_izquierda = fitz.Rect(20, 20, (ancho_hoja / 2) - 10, alto_hoja - 20)
    rect_derecha = fitz.Rect((ancho_hoja / 2) + 10, 20, ancho_hoja - 20, alto_hoja - 20)
    posiciones = [rect_izquierda, rect_derecha]
    
    idx_posicion = 0
    page_actual = None

    for archivo_upload in archivos_subidos:
        # Leemos el archivo directo de la memoria (RAM)
        bytes_pdf = archivo_upload.read()
        doc_item = fitz.open(stream=bytes_pdf, filetype="pdf")
        page_source = doc_item[0] 

        # 1. RECORTE (El que validamos que funciona)
        crop_box = fitz.Rect(10, 10, 410, 590) 
        page_source.set_cropbox(crop_box)

        # 2. CREAR NUEVA HOJA SI TOCA IZQUIERDA
        if idx_posicion == 0:
            page_actual = doc_final.new_page(width=ancho_hoja, height=alto_hoja)

        # 3. PEGAR
        page_actual.show_pdf_page(posiciones[idx_posicion], doc_item, 0, keep_proportion=True)
        
        # 4. AVANZAR
        idx_posicion += 1
        if idx_posicion > 1:
            idx_posicion = 0

    # Guardar en buffer de memoria para descarga
    buffer_salida = io.BytesIO()
    doc_final.save(buffer_salida)
    buffer_salida.seek(0)
    return buffer_salida

# --- INTERFAZ VISUAL ---
st.set_page_config(page_title="Etiquetas A4", layout="centered")

st.title("🖨️ Etiquetas Lado a Lado")
st.write("Subí los PDFs individuales. La app te devuelve un A4 Horizontal listo.")

archivos = st.file_uploader("Seleccioná los archivos", type="pdf", accept_multiple_files=True)

if archivos:
    if st.button("Procesar Etiquetas"):
        with st.spinner('Trabajando...'):
            pdf_bytes = generar_pdf_lado_a_lado(archivos)
            
            st.success(f"¡Listo! Se procesaron {len(archivos)} etiquetas.")
            
            st.download_button(
                label="⬇️ Descargar PDF Final",
                data=pdf_bytes,
                file_name="ETIQUETAS_LISTAS.pdf",
                mime="application/pdf"
            )