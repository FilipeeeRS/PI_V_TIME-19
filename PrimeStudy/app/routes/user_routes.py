from fastapi import APIRouter, Header, status

from app.models.user import User
from app.schemas.token_schemas import TokenResponseSchema
from app.schemas.user_schemas import (
    ApiCompletedResponseSchema,
    UserCreateRequestSchema,
    UserResponseSchema,
    UserUpdateRequestSchema
)


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    summary="Obter usuário atual",
    description="Recupera os dados do usuário associado ao token informado.",
    response_model=UserResponseSchema
)
def get_current_user(
    x_token_login: str = Header(..., alias="X-Token-Login"),
    x_token_password: str = Header(..., alias="X-Token-Password")
):
    """
    Recupera os dados do usuário atual.

    Args:
        x_token_login: Parte identificadora do token.
        x_token_password: Parte complementar do token.

    Returns:
        UserResponseSchema: Dados públicos do usuário.
    """
    user = User(
        name="Example User",
        email="example.user@email.com",
        password_hash="stored_hash"
    )

    return UserResponseSchema(
        uuid=str(user.uuid),
        name=user.name,
        email=user.email
    )


@router.post(
    "",
    summary="Criar novo usuário",
    description="Cria um novo usuário e retorna um token já pronto para uso na API.",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_201_CREATED
)
def create_user(payload: UserCreateRequestSchema):
    """
    Cadastra um novo usuário.

    Args:
        payload: Dados do novo usuário.

    Returns:
        TokenResponseSchema: Token inicial do usuário.
    """
    user = User.create_new(payload.name, payload.email, payload.password)
    token = user.issue_token()

    from datetime import timedelta

    return TokenResponseSchema(
        login=token.login,
        password=token.password,
        expires_at=token.expires_at,
        renewal_recommended_at=token.expires_at - timedelta(hours=1)
    )


@router.put(
    "/me",
    summary="Alterar usuário atual",
    description="Atualiza os dados do usuário vinculado ao token informado.",
    response_model=ApiCompletedResponseSchema
)
def update_current_user(
    payload: UserUpdateRequestSchema,
    x_token_login: str = Header(..., alias="X-Token-Login"),
    x_token_password: str = Header(..., alias="X-Token-Password")
):
    """
    Atualiza os dados do usuário atual.

    Args:
        payload: Dados de atualização.
        x_token_login: Parte identificadora do token.
        x_token_password: Parte complementar do token.

    Returns:
        ApiCompletedResponseSchema: Resposta de conclusão.
    """
    return ApiCompletedResponseSchema(message="Completed")


@router.delete(
    "/me",
    summary="Deletar usuário atual",
    description="Remove o usuário vinculado ao token informado.",
    response_model=ApiCompletedResponseSchema
)
def delete_current_user(
    x_token_login: str = Header(..., alias="X-Token-Login"),
    x_token_password: str = Header(..., alias="X-Token-Password")
):
    """
    Remove o usuário atual.

    Args:
        x_token_login: Parte identificadora do token.
        x_token_password: Parte complementar do token.

    Returns:
        ApiCompletedResponseSchema: Resposta de conclusão.
    """
    return ApiCompletedResponseSchema(message="Completed")