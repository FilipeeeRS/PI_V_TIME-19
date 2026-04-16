from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreateRequestSchema(BaseModel):
    """
    Modelo de entrada para criação de usuário.
    """

    name: str = Field(..., description="Nome do novo usuário.")
    email: EmailStr = Field(..., description="Email do novo usuário.")
    password: str = Field(..., description="Senha em texto puro do novo usuário.")


class UserUpdateRequestSchema(BaseModel):
    """
    Modelo de entrada para atualização parcial do usuário.
    """

    new_name: Optional[str] = Field(None, description="Novo nome do usuário.")
    new_email: Optional[EmailStr] = Field(None, description="Novo email do usuário.")
    new_password: Optional[str] = Field(None, description="Nova senha em texto puro.")


class UserResponseSchema(BaseModel):
    """
    Modelo de saída contendo informações públicas do usuário.
    """

    uuid: str = Field(..., description="Identificador único do usuário.")
    name: str = Field(..., description="Nome do usuário.")
    email: EmailStr = Field(..., description="Email do usuário.")


class ApiCompletedResponseSchema(BaseModel):
    """
    Modelo de resposta para operações concluídas.
    """

    message: str = Field(..., description="Mensagem informando que a operação foi concluída.")