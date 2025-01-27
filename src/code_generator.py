import os
from .model.uml_model import UMLClass, UMLAttribute, UMLMethod

class JavaCodeGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate(self, classes: list[UMLClass]):
        """
        Génère des fichiers Java pour une liste de classes UML.
        """
        for uml_class in classes:
            try:
                self._generate_class_file(uml_class)
            except Exception as e:
                print(f"Erreur lors de la génération de la classe {uml_class.name}: {e}")

    def _generate_class_file(self, uml_class: UMLClass):
        """
        Génère un fichier Java pour une classe UML donnée.
        """
        file_path = os.path.join(self.output_dir, f"{uml_class.name}.java")
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self._generate_class_code(uml_class))
        except Exception as e:
            raise RuntimeError(f"Impossible d'écrire le fichier {file_path}: {e}")

    def _generate_class_code(self, uml_class: UMLClass) -> str:
        """
        Génère le code Java complet pour une classe UML.
        """
        lines = []

        # Ajout du package et des imports (personnalisables)
        lines.append("//package com.example.myproject;")
        lines.append("")
        lines.append("//import java.util.*;")
        lines.append("")

        # Déclaration de la classe
        lines.append(self._generate_class_declaration(uml_class))
        lines.append("{")

        # Attributs
        lines.extend(self._generate_attributes(uml_class))
        lines.append("")

        # Constructeur par défaut
        lines.append(self._generate_default_constructor(uml_class))
        lines.append("")

        # Getters et Setters
        lines.extend(self._generate_getters_and_setters(uml_class))
        lines.append("")

        # Méthodes
        lines.extend(self._generate_methods(uml_class))
        lines.append("")

        # Relations (ajoutées comme commentaires pour une meilleure documentation)
        lines.extend(self._generate_relations_comments(uml_class))

        # Fin de la classe
        lines.append("}")

        return "\n".join(lines)

    def _generate_class_declaration(self, uml_class: UMLClass) -> str:
        """
        Génère la déclaration de la classe.
        """
        parts = ["public"]

        if uml_class.is_abstract:
            parts.append("abstract")

        parts.append("class")
        parts.append(uml_class.name)

        if uml_class.superclasses:
            parts.append("extends " + ", ".join(uml_class.superclasses))

        if uml_class.interfaces:
            parts.append("implements " + ", ".join(uml_class.interfaces))

        return " ".join(parts)

    def _generate_attributes(self, uml_class: UMLClass) -> list[str]:
        """
        Génère les déclarations d'attributs.
        """
        lines = []
        for attr in uml_class.attributes:
            lines.append(f"    private {attr.type} {attr.name};")
        return lines

    def _generate_default_constructor(self, uml_class: UMLClass) -> str:
        """
        Génère un constructeur par défaut.
        """
        return f"""    public {uml_class.name}() {{
        // Constructeur par défaut
    }}"""

    def _generate_getters_and_setters(self, uml_class: UMLClass) -> list[str]:
        """
        Génère les getters et setters pour chaque attribut.
        """
        lines = []
        for attr in uml_class.attributes:
            lines.append(self._generate_getter(attr))
            lines.append(self._generate_setter(attr))
        return lines

    def _generate_getter(self, attr: UMLAttribute) -> str:
        """
        Génère un getter pour un attribut.
        """
        return f"""    public {attr.type} get{attr.name.capitalize()}() {{
        return {attr.name};
    }}"""

    def _generate_setter(self, attr: UMLAttribute) -> str:
        """
        Génère un setter pour un attribut.
        """
        return f"""    public void set{attr.name.capitalize()}({attr.type} {attr.name}) {{
        this.{attr.name} = {attr.name};
    }}"""

    def _generate_methods(self, uml_class: UMLClass) -> list[str]:
        """
        Génère les méthodes pour une classe UML.
        """
        lines = []
        for method in uml_class.methods:
            lines.append(self._generate_method(method))
        return lines

    def _generate_method(self, method: UMLMethod) -> str:
        """
        Génère le code pour une méthode.
        """
        params = [f"{param_type} {param_name}" for param_name, param_type in method.parameters]
        method_str = f"    {method.visibility} {method.return_type} {method.name}({', '.join(params)}) {{"

        if method.return_type != "void":
            default_return = self._get_default_return_value(method.return_type)
            method_str += f"\n        return {default_return};"

        method_str += "\n    }"
        return method_str

    def _get_default_return_value(self, return_type: str) -> str:
        """
        Renvoie une valeur de retour par défaut pour un type donné.
        """
        if return_type in ["int", "long", "short", "byte"]:
            return "0"
        elif return_type in ["float", "double"]:
            return "0.0"
        elif return_type == "boolean":
            return "false"
        return "null"

    def _generate_relations_comments(self, uml_class: UMLClass) -> list[str]:
        """
        Ajoute des relations comme commentaires dans le code généré.
        """
        lines = []
        for relation in uml_class.relations:
            lines.append(f"    // Relation: {relation.type} with {relation.target_id}")
        return lines
