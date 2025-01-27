from src.drawio_parser import DrawIOParser
from src.code_generator import JavaCodeGenerator
from src.model.uml_model import UMLClass, UMLAttribute, UMLMethod, UMLRelation
import os

DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated', 'java')

def main(drawio_file_path: str):
    output_dir = DEFAULT_OUTPUT_DIR

    os.makedirs(output_dir, exist_ok=True)

    parser = DrawIOParser()
    uml_classes = parser.parse(drawio_file_path)

    generator = JavaCodeGenerator(output_dir)
    generator.generate(uml_classes)

    print(f"Les fichiers Java ont été générés dans : {output_dir}")

if __name__ == "__main__":
    drawio_file = input("Entrez le chemin du fichier .drawio : ").strip()

    # Vérifier si le fichier existe
    if not os.path.isfile(drawio_file):
        print(f"Erreur : Le fichier spécifié '{drawio_file}' n'existe pas.")
        exit(1)

    main(drawio_file)
