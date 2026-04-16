from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter

from app.models.token import Token
from app.models.user import User
from app.schemas.token_schemas import TokenRequestSchema, TokenResponseSchema


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/token",
    summary="Criar token temporário de acesso",
    description=(
        "Recebe credenciais do usuário e gera um token temporário com validade de um dia. "
        "Recomenda-se renovação a cada 23 horas."
    ),
    response_model=TokenResponseSchema
)
def create_access_token(payload: TokenRequestSchema):
    """
    Gera um token temporário para autenticação.

    Esta implementação é apenas demonstrativa e não realiza consulta real ao banco de dados.

    Args:
        payload: Credenciais fornecidas pelo usuário.

    Returns:
        TokenResponseSchema: Dados do token emitido.
    """
    fake_user = User.create_new(payload.username, f"{payload.username}@example.com", payload.password)
    token = fake_user.issue_token()

    return TokenResponseSchema(
        login=token.login,
        password=token.password,
        expires_at=token.expires_at,
        renewal_recommended_at=token.expires_at - timedelta(hours=1)
    )


@router.post(
    "/token/renew",
    summary="Renovar token temporário",
    description="Renova o token temporário atualmente utilizado pelo usuário.",
    response_model=TokenResponseSchema
)
def renew_access_token():
    """
    Renova um token temporário de autenticação.

    Returns:
        TokenResponseSchema: Novo token emitido.
    """
    renewed = Token.create_temporary_token(uuid4())

    return TokenResponseSchema(
        login=renewed.login,
        password=renewed.password,
        expires_at=renewed.expires_at,
        renewal_recommended_at=renewed.expires_at - timedelta(hours=1)
    )