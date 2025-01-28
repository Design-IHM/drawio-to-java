from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flasgger import Swagger
import os
import shutil
from werkzeug.utils import secure_filename
import zipfile
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.drawio_parser import DrawIOParser
from src.code_generator import JavaCodeGenerator

app = Flask(__name__)
CORS(app, origins=["https://drawio-to-java.vercel.app", "https://drawio-to-java-production.up.railway.app"])

# Configurer Swagger
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API Documentation",
        "description": "Documentation interactive des endpoints de votre API.",
        "version": "1.0.0",
    },
    "host": "localhost:5000",
    "schemes": ["http", "https"]
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/",
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Définir les répertoires d'upload et de génération
UPLOAD_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
OUTPUT_DIR = os.path.join(UPLOAD_DIR, 'generated')
ZIP_PATH = os.path.join(UPLOAD_DIR, 'generated.zip')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route('/upload', methods=['POST'])
def upload_drawio():
    """
    Gérer l'upload d'un fichier DrawIO et générer le code Java.
    ---
    tags:
      - Upload
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Le fichier DrawIO à convertir en code Java.
    responses:
      200:
        description: Conversion réussie, le fichier ZIP est prêt.
      400:
        description: Erreur d'upload ou fichier invalide.
      500:
        description: Erreur interne du serveur.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400

    drawio_file = request.files['file']

    if drawio_file.filename == '':
        return jsonify({'error': 'Nom de fichier invalide'}), 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filename = secure_filename(drawio_file.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)
    drawio_file.save(file_path)

    try:
        parser = DrawIOParser()
        uml_classes = parser.parse(file_path)

        generator = JavaCodeGenerator(OUTPUT_DIR)
        generator.generate(uml_classes)

        with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(OUTPUT_DIR):
                for file in files:
                    file_full_path = os.path.join(root, file)
                    zipf.write(file_full_path, os.path.relpath(file_full_path, OUTPUT_DIR))

        os.remove(file_path)
        return jsonify({'message': 'Conversion réussie, téléchargez le fichier ZIP à l\'URL /download'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download', methods=['GET'])
def download_zip():
    """
    Permettre au client de télécharger le fichier ZIP généré.
    ---
    tags:
      - Download
    responses:
      200:
        description: Le fichier ZIP contenant le code généré.
      404:
        description: Aucun fichier à télécharger.
    """
    if not os.path.exists(ZIP_PATH):
        return jsonify({'error': 'Aucun fichier à télécharger'}), 404

    response = send_file(ZIP_PATH, as_attachment=True)

    try:
        shutil.rmtree(OUTPUT_DIR)
        os.remove(ZIP_PATH)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    except Exception as e:
        print(f"Erreur lors du nettoyage des fichiers : {e}")

    return response


@app.route('/', methods=['GET'])
def documentation():
    """
    Redirige vers la documentation Swagger.
    ---
    tags:
      - Documentation
    responses:
      200:
        description: Page de documentation interactive.
    """
    return jsonify({"message": "Visitez /apidocs pour la documentation Swagger."})


if __name__ == '__main__':
    app.run(debug=False)
