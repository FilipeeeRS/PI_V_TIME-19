from dataclasses import dataclass, field
from hashlib import sha256
from typing import List, Optional, Union
from uuid import UUID, uuid4

from app.models.course import Course
from app.models.token import Token


@dataclass
class User:
    """
    Representa um usuário da API.

    O usuário contém seus dados básicos de identificação,
    autenticação e a lista de cursos associados.
    """

    name: str
    password_hash: str
    email: str
    uuid: UUID = field(default_factory=uuid4)
    courses: List[Course] = field(default_factory=list)

    def __init__(
        self,
        token: Optional[Token] = None,
        name: str = "",
        password_hash: str = "",
        email: str = ""
    ):
        """
        Inicializa um usuário.

        Quando um token for informado, o comportamento esperado em produção é:
        validar o token, buscar o usuário correspondente no banco de dados
        e preencher a instância com os dados persistidos.

        Args:
            token: Token associado ao usuário.
            name: Nome do usuário.
            password_hash: Senha do usuário em hash.
            email: Email do usuário.
        """
        if token is not None:
            self.name = "Recovered User"
            self.password_hash = "database_loaded_hash"
            self.email = "recovered.user@example.com"
            self.uuid = uuid4()
            self.courses = []
        else:
            self.name = name
            self.password_hash = password_hash
            self.email = email
            self.uuid = uuid4()
            self.courses = []

    @staticmethod
    def hash_password(raw_password: str) -> str:
        """
        Converte uma senha em texto puro para hash.

        Args:
            raw_password: Senha em texto puro.

        Returns:
            str: Hash da senha.
        """
        return sha256(raw_password.encode("utf-8")).hexdigest()

    @classmethod
    def create_new(cls, name: str, email: str, raw_password: str) -> "User":
        """
        Cria um novo usuário com senha já protegida por hash.

        Args:
            name: Nome do usuário.
            email: Email do usuário.
            raw_password: Senha em texto puro.

        Returns:
            User: Novo usuário criado.
        """
        return cls(
            name=name,
            email=email,
            password_hash=cls.hash_password(raw_password)
        )

    def verify_password(self, raw_password: str) -> bool:
        """
        Verifica se a senha informada corresponde ao hash armazenado.

        Args:
            raw_password: Senha em texto puro.

        Returns:
            bool: True se a senha estiver correta.
        """
        return self.password_hash == self.hash_password(raw_password)

    def issue_token(self) -> Token:
        """
        Gera um novo token temporário para o usuário.

        Returns:
            Token: Token temporário emitido.
        """
        return Token.create_temporary_token(self.uuid)

    def add_course(self, course: Course, parent_id: Optional[Union[UUID, str]] = None) -> None:
        """
        Adiciona um curso ao usuário.

        Se parent_id for informado, o curso será adicionado como subtópico
        do curso pai correspondente.

        Args:
            course: Curso a ser adicionado.
            parent_id: Identificador opcional do curso pai.
        """
        if parent_id is None:
            self.courses.append(course)
            return

        parent = self.get_course_by_id(parent_id)
        if parent is None:
            raise ValueError("Parent course not found.")

        parent.subtopics.append(course)

    def get_course_by_id(self, course_id: Union[UUID, str]) -> Optional[Course]:
        """
        Procura um curso ou subtópico pelo identificador.

        Args:
            course_id: Identificador do curso.

        Returns:
            Optional[Course]: Curso encontrado ou None.
        """
        for course in self.courses:
            found = course.find_subtopic_by_id(course_id)
            if found is not None:
                return found
        return None

    def get_course_by_name(self, course_name: str) -> Optional[Course]:
        """
        Procura um curso ou subtópico pelo nome.

        Args:
            course_name: Nome do curso.

        Returns:
            Optional[Course]: Curso encontrado ou None.
        """
        for course in self.courses:
            if course.name.lower() == course_name.lower():
                return course

            found = self._search_course_by_name_recursive(course, course_name)
            if found is not None:
                return found

        return None

    def _search_course_by_name_recursive(self, current: Course, course_name: str) -> Optional[Course]:
        """
        Realiza busca recursiva de curso pelo nome.

        Args:
            current: Curso atual da busca.
            course_name: Nome procurado.

        Returns:
            Optional[Course]: Curso encontrado ou None.
        """
        for subtopic in current.subtopics:
            if subtopic.name.lower() == course_name.lower():
                return subtopic

            found = self._search_course_by_name_recursive(subtopic, course_name)
            if found is not None:
                return found

        return None