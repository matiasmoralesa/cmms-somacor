import PyPDF2
import json
import os

pdf_files = [
    "Check_List_camión supersucker.pdf",
    "F-PR-020-CH01 Check List Camionetas MDO.pdf",
    "F-PR-034-CH01_Check Retroexcavadora MDO.pdf",
    "F-PR-037-CH01 Check List Cargador Frontal MDO.pdf",
    "F-PR-040-CH01 Check List Minicargador MDO.pdf"
]

for pdf_file in pdf_files:
    if os.path.exists(pdf_file):
        print(f"\n{'='*80}")
        print(f"ARCHIVO: {pdf_file}")
        print('='*80)
        
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                print(f"Número de páginas: {len(pdf_reader.pages)}\n")
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    print(f"\n--- Página {page_num + 1} ---")
                    print(text)
                    
        except Exception as e:
            print(f"Error al leer {pdf_file}: {e}")
    else:
        print(f"Archivo no encontrado: {pdf_file}")
