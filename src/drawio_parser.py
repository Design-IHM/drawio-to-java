import re
import xml.etree.ElementTree as ET
from .model.uml_model import UMLClass, UMLAttribute, UMLMethod, UMLRelation


class DrawIOParser:
    def __init__(self):
        self.namespace = {'xmlns': 'http://www.w3.org/1999/xhtml'}

    def parse(self, file_path: str) -> list[UMLClass]:
        """
        Parse un fichier .drawio et retourne une liste de classes UML
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            cells = root.findall(".//mxCell")

            classes = {}
            relations = []

            # Analyse des classes et relations
            for cell in cells:
                if self._is_class(cell):
                    uml_class = self._parse_class(cell)
                    classes[cell.get('id')] = uml_class
                elif self._is_relation(cell):
                    relations.append(self._parse_relation(cell))

            # Analyse des attributs/méthodes pour chaque classe
            for cell in cells:
                if self._is_attribute_or_method(cell):
                    parent_id = cell.get('parent')
                    if parent_id in classes:
                        self._process_attribute_or_method(classes[parent_id], cell)

            # Ajout des relations (héritage ou autre)
            self._process_relations(relations, classes)

            return list(classes.values())

        except ET.ParseError:
            raise ValueError("Le fichier n'est pas un fichier Draw.io valide.")
        except Exception as e:
            raise ValueError(f"Erreur lors de l'analyse du fichier : {e}")

    def _is_class(self, cell) -> bool:
        style = cell.get('style', '')
        return 'swimlane' in style and cell.get('vertex') == '1'

    def _is_relation(self, cell) -> bool:
        return cell.get('edge') == '1'

    def _is_attribute_or_method(self, cell) -> bool:
        value = cell.get('value', '').strip()
        return value and cell.get('vertex') == '1' and 'swimlane' not in cell.get('style', '')

    def _parse_class(self, cell) -> UMLClass:
        class_name = self._clean_value(cell.get('value', '').split('\n')[0].strip())
        return UMLClass(class_name)

    def _process_attribute_or_method(self, uml_class: UMLClass, cell):
        value = self._clean_value(cell.get('value', '').strip())

        # Déterminer si c'est une méthode ou un attribut
        if '(' in value:
            uml_class.add_method(self._parse_method(value))
        elif ':' in value:
            uml_class.add_attribute(self._parse_attribute(value))

    def _parse_attribute(self, attr_string: str) -> UMLAttribute:
        attr_string = self._clean_value(attr_string)
        parts = attr_string.split(':')
        name = parts[0].strip()
        type_ = parts[1].strip() if len(parts) > 1 else "String"

        visibility = self._extract_visibility(name)

        # Nettoyage des noms pour supprimer les caractères invalides
        name = self._sanitize_java_name(name)

        return UMLAttribute(name, type_, visibility)

    def _parse_method(self, method_string: str) -> UMLMethod:
        method_string = self._clean_value(method_string)
        parts = method_string.split('(')
        name = parts[0].strip()

        visibility = self._extract_visibility(name)

        # Nettoyage des noms pour supprimer les caractères invalides
        name = self._sanitize_java_name(name)

        return_type = "void"
        parameters = []

        if len(parts) > 1:
            param_section = parts[1].split(')')[0]
            if param_section:
                param_pairs = param_section.split(',')
                for param in param_pairs:
                    param_parts = param.strip().split(':')
                    if len(param_parts) == 2:
                        param_name = self._sanitize_java_name(param_parts[0].strip())
                        param_type = param_parts[1].strip()
                        parameters.append((param_name, param_type))

            if ':' in parts[1]:
                return_type = parts[1].split(':')[1].strip().split(')')[0]

        return UMLMethod(name, return_type, parameters, visibility)

    def _parse_relation(self, cell) -> UMLRelation:
        source_id = cell.get('source')
        target_id = cell.get('target')
        style = cell.get('style', '')

        relation_type = self._determine_relation_type(style)

        return UMLRelation(source_id, target_id, relation_type)

    def _determine_relation_type(self, style: str) -> str:
        if 'endArrow=diamond' in style:
            return "composition"
        elif 'endArrow=diamondThin' in style:
            return "aggregation"
        elif 'endArrow=block' in style:
            return "inheritance"
        else:
            return "association"

    def _process_relations(self, relations: list[UMLRelation], classes: dict):
        for relation in relations:
            if relation.source_id in classes and relation.target_id in classes:
                source_class = classes[relation.source_id]
                target_class = classes[relation.target_id]

                if relation.type == "inheritance":
                    source_class.add_superclass(target_class.name)
                else:
                    source_class.add_relation(relation.type, target_class.name)

    def _clean_value(self, value: str) -> str:
        """
        Nettoie une valeur en supprimant les balises HTML et en normalisant les espaces
        """
        value = re.sub(r'<[^>]*>', '', value)  # Supprimer les balises HTML
        return value.strip()

    def _extract_visibility(self, name: str) -> str:
        """
        Extrait la visibilité à partir du préfixe du nom (+, -, #).
        """
        if name.startswith('+'):
            return "public"
        elif name.startswith('-'):
            return "private"
        elif name.startswith('#'):
            return "protected"
        return "private"

    def _sanitize_java_name(self, name: str) -> str:
        """
        Supprime les caractères non valides pour un identifiant Java.
        """
        return re.sub(r'[^\w]', '', name)
