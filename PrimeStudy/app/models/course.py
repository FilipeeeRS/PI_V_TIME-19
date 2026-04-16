from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union
from uuid import UUID, uuid4


@dataclass
class Course:
    """
    Representa um curso, matéria ou tópico pertencente a um usuário.

    Um curso pode conter subtópicos, permitindo a criação de uma estrutura
    hierárquica de conteúdos.
    """

    name: str
    uuid: Union[UUID, str] = field(default_factory=uuid4)
    last_topic: str = ""
    subtopics: List["Course"] = field(default_factory=list)

    def add_subtopic(self, subtopic_name: str) -> "Course":
        """
        Cria e adiciona um novo subtópico ao curso atual.

        Args:
            subtopic_name: Nome do subtópico.

        Returns:
            Course: Objeto do subtópico criado.
        """
        subtopic_identifier = f"{self.uuid}.{len(self.subtopics) + 1}"
        subtopic = Course(name=subtopic_name, uuid=subtopic_identifier)
        self.subtopics.append(subtopic)
        return subtopic

    def find_subtopic_by_id(self, course_id: Union[UUID, str]) -> Optional["Course"]:
        """
        Procura um curso ou subtópico recursivamente pelo identificador.

        Args:
            course_id: Identificador do curso procurado.

        Returns:
            Optional[Course]: Curso encontrado ou None.
        """
        if str(self.uuid) == str(course_id):
            return self

        for subtopic in self.subtopics:
            found = subtopic.find_subtopic_by_id(course_id)
            if found is not None:
                return found

        return None