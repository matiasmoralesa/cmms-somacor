from docx import Document
import json

# Leer el documento
doc = Document('corregido.docx')

# Extraer todo el texto
texto_completo = []
for para in doc.paragraphs:
    if para.text.strip():
        texto_completo.append(para.text.strip())

# Guardar en archivo de texto
with open('contenido_docx.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(texto_completo))

print(f"✓ Extraídos {len(texto_completo)} párrafos")
print(f"✓ Guardado en: contenido_docx.txt")

# Mostrar primeros párrafos
print("\n" + "="*70)
print("PRIMEROS PÁRRAFOS DEL DOCUMENTO:")
print("="*70)
for i, para in enumerate(texto_completo[:30], 1):
    print(f"\n{i}. {para}")
