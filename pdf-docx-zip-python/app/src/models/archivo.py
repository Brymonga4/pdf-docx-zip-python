import os
import magic
import zipfile
from io import BytesIO
from services.servicio import Metodos

class Archivo:

    def __init__(self, file, folder):
        self.file = file
        self.folder = folder   
        self.path_file = self.set_path_file(folder)              
        self.mime_type = None
        self.compressed_files = []
        self.pdf_list = []
        self.docs_list = []


    def set_path_file_and_save(self, folder):
        """Configura el directorio del archivo y lo guarda a partir de una carpeta donde se subirá."""
        self.path_file = os.path.join(folder, self.file.filename)
        self.save()

    def set_path_file(self,folder):
        """Configura el directorio del archivo a partir de una carpeta donde se subirá."""
        return os.path.join(folder, self.file.filename)

    def save(self):
        """Guarda el archivo, en la carpeta proporcionado en el constructor."""
        self.file.save(self.path_file)

    def what_mime_type_bytes(self):
        """A partir de un directorio de archivo, establece el tipo de MIME en texto plano."""
        try:
            self.save()
            self.mime_type = magic.from_buffer(open(self.path_file, "rb").read(2048), mime=True)
        except TypeError as e:
            print(f"Error: {e}")
            self.mime_type = "application/octet-stream" 


    def process(self):
        """Procesa el archivo del objeto dependiendo del tipo de MIME que tiene."""
        if self.mime_type == 'application/zip' and self.file.filename.endswith('.zip'):
            return self.process_zip()
        elif self.mime_type == 'application/pdf':
            return self.process_pdf()
        elif self.mime_type == 'application/zip'and self.file.filename.endswith('.docx'):
            return self.process_docx()
        else:
            return "Tipo de archivo no aceptado."

    def process_pdf(self):
        """Extrae el texto del directorio del archivo PDF y lo devuelve."""
        return Metodos.text_from_pdf(self.path_file)

    def process_docx(self):
        """Extrae el text del directorio del archivo DOCX y lo devuelve."""
        return Metodos.extract_text_from_docx(self.path_file)

    def process_zip(self):
        """Procesa todos los archivos contenidos en la carpeta zip y los añade a las listas del objeto acordemente."""
        with zipfile.ZipFile(self.path_file, 'r') as zip:
            file_list = zip.namelist()
            for filename in file_list:
                self.compressed_files.append(filename)
                if filename.endswith(".docx"):
                    with zip.open(filename) as zip_file:
                        docx_data = BytesIO(zip_file.read())
                        docx_text = Metodos.extract_text_from_docx(docx_data)
                        self.docs_list.append((filename, docx_text))
                elif filename.endswith(".pdf"):
                    with zip.open(filename) as zip_file:
                        pdf_data = BytesIO(zip_file.read())
                        pdf_text = Metodos.text_from_temp_pdf(pdf_data)
                        self.pdf_list.append((filename, pdf_text))
        return "Zip detectado."