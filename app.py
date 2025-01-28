from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import shutil
from werkzeug.utils import secure_filename
import zipfile
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.drawio_parser import DrawIOParser
from src.code_generator import JavaCodeGenerator

app = Flask(__name__)
CORS(app)  # Autoriser les requêtes depuis le front-end React

# Définir les répertoires d'upload et de génération
UPLOAD_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
OUTPUT_DIR = os.path.join(UPLOAD_DIR, 'generated')
ZIP_PATH = os.path.join(UPLOAD_DIR, 'generated.zip')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_drawio():
    """Gérer l'upload d'un fichier DrawIO et générer le code Java."""
    # Vérifier si un fichier a été envoyé
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400

    drawio_file = request.files['file']

    if drawio_file.filename == '':
        return jsonify({'error': 'Nom de fichier invalide'}), 400

    # Créer les répertoires nécessaires s'ils ont été supprimés
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

        # Création du fichier ZIP
        with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(OUTPUT_DIR):
                for file in files:
                    file_full_path = os.path.join(root, file)
                    zipf.write(file_full_path, os.path.relpath(file_full_path, OUTPUT_DIR))

        # Supprimer le fichier DrawIO après traitement
        os.remove(file_path)

        return jsonify({'message': 'Conversion réussie, téléchargez le fichier ZIP à l\'URL /download'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['GET'])
def download_zip():
    """Permettre au client de télécharger le fichier ZIP généré."""
    if not os.path.exists(ZIP_PATH):
        return jsonify({'error': 'Aucun fichier à télécharger'}), 404

    # Envoyer le fichier ZIP au client
    response = send_file(ZIP_PATH, as_attachment=True)

    try:
        # Nettoyage des fichiers générés
        shutil.rmtree(OUTPUT_DIR)
        os.remove(ZIP_PATH)

        # Recréer les répertoires nécessaires après suppression
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    except Exception as e:
        print(f"Erreur lors du nettoyage des fichiers : {e}")

    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
