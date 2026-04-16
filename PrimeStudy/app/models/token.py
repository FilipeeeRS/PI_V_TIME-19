from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256
from uuid import UUID


@dataclass
class Token:
    """
    Representa um token temporário de acesso à API.

    O token é derivado do identificador do usuário e possui tempo de validade
    limitado. Recomenda-se renovação preventiva antes do vencimento.
    """

    login: str
    password: str
    expires_at: datetime
    hashed_user_reference: str

    @staticmethod
    def _hash_user_reference(user_id: UUID) -> str:
        """
        Gera um hash a partir do identificador do usuário.

        Args:
            user_id: Identificador único do usuário.

        Returns:
            str: Hash derivado do identificador do usuário.
        """
        return sha256(str(user_id).encode("utf-8")).hexdigest()

    @classmethod
    def create_temporary_token(cls, user_id: UUID) -> "Token":
        """
        Cria um token temporário com validade de um dia.

        Args:
            user_id: Identificador do usuário.

        Returns:
            Token: Token criado para autenticação.
        """
        hashed_reference = cls._hash_user_reference(user_id)
        middle = len(hashed_reference) // 2

        return cls(
            login=hashed_reference[:middle],
            password=hashed_reference[middle:],
            expires_at=datetime.utcnow() + timedelta(days=1),
            hashed_user_reference=hashed_reference
        )

    @staticmethod
    def validate(login: str, password: str) -> bool:
        """
        Verifica se os campos mínimos do token foram informados.

        Args:
            login: Parte identificadora do token.
            password: Parte complementar do token.

        Returns:
            bool: True quando os campos existem; False caso contrário.
        """
        return bool(login and password)

    def should_be_renewed(self) -> bool:
        """
        Informa se o token já entrou na janela recomendada de renovação.

        Returns:
            bool: True quando a renovação já é recomendada.
        """
        return datetime.utcnow() >= (self.expires_at - timedelta(hours=1))


Token.TEST_TOKEN = Token(
    login="test_login_value",
    password="test_password_value",
    expires_at=datetime.utcnow() + timedelta(days=1),
    hashed_user_reference="test_user_hash_reference"
)
"""
Token fixo utilizado apenas para testes locais.
Deve ser removido na versão de release.
"""