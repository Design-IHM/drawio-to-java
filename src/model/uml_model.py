from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class UMLAttribute:
    name: str
    type: str
    visibility: str = "private"
    is_static: bool = False
    is_final: bool = False

@dataclass
class UMLMethod:
    name: str
    return_type: str
    parameters: List[Tuple[str, str]] = field(default_factory=list)
    visibility: str = "public"
    is_static: bool = False
    is_abstract: bool = False

@dataclass
class UMLRelation:
    source_id: str
    target_id: str
    type: str  # "inheritance", "composition", "aggregation", "association"

@dataclass
class UMLClass:
    name: str
    attributes: List[UMLAttribute] = field(default_factory=list)
    methods: List[UMLMethod] = field(default_factory=list)
    superclasses: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    relations: List[UMLRelation] = field(default_factory=list)
    is_abstract: bool = False
    is_interface: bool = False
    package: str = ""

    def add_attribute(self, attribute: UMLAttribute):
        self.attributes.append(attribute)

    def add_method(self, method: UMLMethod):
        self.methods.append(method)

    def add_superclass(self, superclass: str):
        self.superclasses.append(superclass)

    def add_relation(self, relation_type: str, target_class: str):
        self.relations.append(UMLRelation("", target_class, relation_type))
