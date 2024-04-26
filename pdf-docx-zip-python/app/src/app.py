from flask import Flask, redirect, request, render_template, send_file, url_for
from flask_bootstrap import Bootstrap
import os
from models.archivo import Archivo
from services.servicio import Metodos

app = Flask(__name__)
Bootstrap(app)	
UPLOAD_FOLDER = '/uploads' # Path de la carpeta donde se suben los archivos
TEMP_FILES_FOLDER = '/temp'  # Path de la carpeta donde se suben los archivos temporales


UPLOAD_FOLDER = os.path.join(app.root_path, 'uploaded_files') 
TEMP_FILES_FOLDER = os.path.join(app.root_path, 'Temp Files')
# Comprobamos si existe y si no creamos los directorios
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(TEMP_FILES_FOLDER):
    os.makedirs(TEMP_FILES_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Configurar la carpeta donde subir los archivos

@app.route('/')
def index():
    return render_template('pdf_file.html')

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

@app.route('/docx_file')
def docx_file():
    return render_template('docx_file.html')

@app.route('/pdf_file')
def pdf_file():
    return render_template('pdf_file.html')

@app.route('/zip_file')
def zip_file():
    return render_template('zip_file.html')

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

@app.route('/process_zip', methods=['POST'])
def process_zip():

    text = "Archivo no soportado."

    file = request.files['file']

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

    return render_template('zip_processed.html', message=text, files_list=archivo.compressed_files, pdf_list=archivo.pdf_list, docs_list=archivo.docs_list)   

@app.route('/process_pdf_to_text', methods=['POST'])
def process_pdf_to_text():
    to_file = "text"
    text=''
    file = request.files['file']
    archivo = Archivo(file, UPLOAD_FOLDER)
    archivo.what_mime_type_bytes()
    text = archivo.process()
    return render_template('file_processed.html', title=file.filename, text=text, to_file=to_file)

@app.route('/process_docx_to_text', methods=['POST'])
def process_docx_to_text():
    to_file = "text"
    text=''
    file = request.files['file']
    archivo = Archivo(file, UPLOAD_FOLDER)
    archivo.what_mime_type_bytes()
    print(archivo.mime_type)
    text = archivo.process()
    return render_template('file_processed.html', title=file.filename, text=text, to_file=to_file)


@app.route('/process_pdf_to_docx', methods=['POST'])
def process_pdf_to_docx():
    to_file = "docx"
    text=''
    file = request.files['file']
    archivo = Archivo(file, UPLOAD_FOLDER)
    archivo.what_mime_type_bytes()
    text = archivo.process()
    Metodos.create_docx_from_text(text, UPLOAD_FOLDER, archivo.file.filename)
    # send_file(archivo.path_file, as_attachment=True, download_name=archivo.file.filename)
    return render_template('file_processed.html', title=file.filename, text=text, to_file=to_file)

@app.route('/process_pdf_extract_img', methods=['POST'])
def process_pdf_extract_img():
    text=""
    to_file ="img"
    file = request.files['file']
    archivo = Archivo(file, UPLOAD_FOLDER)
    archivo.what_mime_type_bytes()

    img_folder_path = os.path.join(UPLOAD_FOLDER, os.path.splitext(os.path.basename(archivo.path_file))[0])
    if not os.path.exists(img_folder_path):
        os.makedirs(img_folder_path)

    imgs = Metodos.extract_img_from_pdf(archivo.path_file)

    for i, img in enumerate(imgs):
        img_filename = os.path.join(img_folder_path, f'image_{i}.png')
        with open(img_filename, 'wb') as f:
            f.write(img.getvalue())
    return render_template('file_processed.html', title=file.filename, text=text, to_file=to_file)


@app.route('/process_pdf_to_img', methods=['POST'])
def process_pdf_to_img():
    text=""
    to_file ="img"
    file = request.files['file']
    archivo = Archivo(file, UPLOAD_FOLDER)
    archivo.what_mime_type_bytes()

    img_folder_path = os.path.join(UPLOAD_FOLDER, os.path.splitext(os.path.basename(archivo.path_file))[0])
    if not os.path.exists(img_folder_path):
        os.makedirs(img_folder_path)

    imgs = Metodos.transform_entire_pdf_to_png(archivo.path_file)

    for i, pixmap in enumerate(imgs):
        img_filename = os.path.join(img_folder_path, f'image_{i}.png')
        pixmap.save(img_filename)

    return render_template('file_processed.html', title=file.filename, text=text, to_file=to_file)
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
