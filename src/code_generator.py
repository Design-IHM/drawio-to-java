import os
from .model.uml_model import UMLClass

class JavaCodeGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    # Génération des fichiers Java pour chaque classe UML
    def generate(self, classes: list[UMLClass]):
        for uml_class in classes:
            self._generate_class_file(uml_class)

    def _generate_class_file(self, uml_class: UMLClass):
        file_path = os.path.join(self.output_dir, f"{uml_class.name}.java")

        with open(file_path, 'w') as file:
            file.write(self._generate_class_code(uml_class))

    def _generate_class_code(self, uml_class: UMLClass) -> str:
        lines = []

        # Ajout du package
        lines.append("//package com.example.myproject;")
        lines.append("")

        # Ajout des imports
        lines.append("//import java.util.*;")
        lines.append("")

        # Déclaration de la classe
        lines.append(self._generate_class_declaration(uml_class))
        lines.append("{")

        # Attributs avec commentaires
        for attr in uml_class.attributes:
            lines.append(f"    private {attr.type} {attr.name};")
        lines.append("")

        # Constructeur par défaut
        lines.append(f"    public {uml_class.name}() {{")
        lines.append("    }")
        lines.append("")

        # Getters et Setters
        for attr in uml_class.attributes:
            lines.append(self._generate_getter(attr))
            lines.append("")
            lines.append(self._generate_setter(attr))
            lines.append("")

        # Méthodes
        for method in uml_class.methods:
            lines.append(self._generate_method(method))
            lines.append("")

        # Relations (si définies)
        for relation in uml_class.relations:
            lines.append(f"    // Relation: {relation.type} with {relation.target_id}")
        lines.append("")

        # Fin de la classe
        lines.append("}")

        return "\n".join(lines)

    def _generate_class_declaration(self, uml_class: UMLClass) -> str:
        """
        Génère la déclaration de la classe
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

    def _generate_getter(self, attr) -> str:
        """
        Génère le getter pour un attribut
        """
        return f"""    public {attr.type} get{attr.name.capitalize()}() {{
        return {attr.name};
    }}"""

    def _generate_setter(self, attr) -> str:
        """
        Génère le setter pour un attribut
        """
        return f"""    public void set{attr.name.capitalize()}({attr.type} {attr.name}) {{
        this.{attr.name} = {attr.name};
    }}"""

    def _generate_method(self, method) -> str:
        """
        Génère le code pour une méthode
        """
        params = []
        for param_name, param_type in method.parameters:
            params.append(f"{param_type} {param_name}")

        method_str = f"    {method.visibility} {method.return_type} {method.name}({', '.join(params)}) {{"

        # Ajouter un return par défaut si nécessaire
        if method.return_type != "void":
            if method.return_type in ["int", "long", "short", "byte"]:
                method_str += "\n        return 0;"
            elif method.return_type in ["float", "double"]:
                method_str += "\n        return 0.0;"
            elif method.return_type == "boolean":
                method_str += "\n        return false;"
            else:
                method_str += "\n        return null;"

        method_str += "\n    }"
        return method_str
