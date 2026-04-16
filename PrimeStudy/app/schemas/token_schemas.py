from datetime import datetime
from pydantic import BaseModel, Field


class TokenRequestSchema(BaseModel):
    """
    Modelo de entrada para autenticação.
    """

    username: str = Field(..., description="Nome do usuário para autenticação.")
    password: str = Field(..., description="Senha em texto puro do usuário.")


class TokenResponseSchema(BaseModel):
    """
    Modelo de resposta contendo os dados do token.
    """

    login: str = Field(..., description="Campo de autenticação do token.")
    password: str = Field(..., description="Campo complementar do token.")
    expires_at: datetime = Field(..., description="Data de expiração do token.")
    renewal_recommended_at: datetime = Field(..., description="Momento recomendado para renovação preventiva.")