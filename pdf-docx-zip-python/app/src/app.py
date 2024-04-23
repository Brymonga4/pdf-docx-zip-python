from flask import Flask, request, render_template
import os
from models.archivo import Archivo

app = Flask(__name__)

UPLOAD_FOLDER = '/uploads' # Path de la carpeta donde se suben los archivos
TEMP_FILES_FOLDER = '/temp'  # Path de la carpeta donde se suben los archivos temporales


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Configurar la carpeta donde subir los archivos

@app.route('/')
def index():
    return render_template('index.html')

# Subir Archivos
@app.route('/upload_file', methods=['POST'])
def upload_file():

    text = "Archivo no soportado."

    file = request.files['file']

    print(f"File: {file}")

    if file.filename == '':
        return render_template('index.html', message='No se ha subido ningún archivo.')
    
    archivo = Archivo(file, UPLOAD_FOLDER)
    archivo.what_mime_type_bytes()
    print (f"ARCHIVO: {archivo.mime_type}")

    text = archivo.process()

    if not archivo.pdf_list:
        archivo.pdf_list =[("No hay PDF en la carpeta","Vacío")]
    if not archivo.docs_list:
        archivo.docs_list =[("No hay DOCx en la carpeta","Vacío")]

    return render_template('file_type.html', message=text, files_list=archivo.compressed_files, pdf_list=archivo.pdf_list, docs_list=archivo.docs_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8086, debug=True)
