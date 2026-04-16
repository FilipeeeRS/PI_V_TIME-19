from uuid import uuid4

from fastapi import APIRouter, Header

from app.schemas.course_schemas import (
    CourseCreateRequestSchema,
    CourseResponseSchema,
    CourseUpdateRequestSchema
)
from app.schemas.user_schemas import ApiCompletedResponseSchema


router = APIRouter(prefix="/users/me/courses", tags=["User Courses"])


@router.post(
    "",
    summary="Adicionar novo curso",
    description=(
        "Adiciona um novo curso ao usuário autenticado. "
        "Se um curso pai for informado, o novo curso será criado como subtópico."
    ),
    response_model=ApiCompletedResponseSchema
)
def add_course_to_current_user(
    payload: CourseCreateRequestSchema,
    x_token_login: str = Header(..., alias="X-Token-Login"),
    x_token_password: str = Header(..., alias="X-Token-Password")
):
    """
    Adiciona um curso ao usuário atual.

    Args:
        payload: Dados do novo curso.
        x_token_login: Parte identificadora do token.
        x_token_password: Parte complementar do token.

    Returns:
        ApiCompletedResponseSchema: Resposta de conclusão.
    """
    return ApiCompletedResponseSchema(message="Completed")


@router.get(
    "/by-id/{course_id}",
    summary="Buscar curso por identificador",
    description="Recupera um curso específico do usuário com base em seu identificador.",
    response_model=CourseResponseSchema
)
def get_course_by_id(
    course_id: str,
    x_token_login: str = Header(..., alias="X-Token-Login"),
    x_token_password: str = Header(..., alias="X-Token-Password")
):
    """
    Busca um curso pelo identificador.

    Args:
        course_id: Identificador do curso.
        x_token_login: Parte identificadora do token.
        x_token_password: Parte complementar do token.

    Returns:
        CourseResponseSchema: Dados do curso.
    """
    return CourseResponseSchema(
        uuid=course_id,
        name="Sample Course",
        last_topic="Introduction",
        subtopics_count=2
    )


@router.get(
    "/by-name/{course_name}",
    summary="Buscar curso por nome",
    description="Recupera um curso específico do usuário com base em seu nome.",
    response_model=CourseResponseSchema
)
def get_course_by_name(
    course_name: str,
    x_token_login: str = Header(..., alias="X-Token-Login"),
    x_token_password: str = Header(..., alias="X-Token-Password")
):
    """
    Busca um curso pelo nome.

    Args:
        course_name: Nome do curso.
        x_token_login: Parte identificadora do token.
        x_token_password: Parte complementar do token.

    Returns:
        CourseResponseSchema: Dados do curso.
    """
    return CourseResponseSchema(
        uuid=str(uuid4()),
        name=course_name,
        last_topic="Current Topic",
        subtopics_count=0
    )


@router.patch(
    "/{course_id}",
    summary="Alterar curso rapidamente",
    description="Atualiza parcialmente um curso do usuário autenticado.",
    response_model=ApiCompletedResponseSchema
)
def update_course(
    course_id: str,
    payload: CourseUpdateRequestSchema,
    x_token_login: str = Header(..., alias="X-Token-Login"),
    x_token_password: str = Header(..., alias="X-Token-Password")
):
    """
    Atualiza um curso do usuário.

    Args:
        course_id: Identificador do curso.
        payload: Alterações desejadas.
        x_token_login: Parte identificadora do token.
        x_token_password: Parte complementar do token.

    Returns:
        ApiCompletedResponseSchema: Resposta de conclusão.
    """
    return ApiCompletedResponseSchema(message="Completed")


@router.delete(
    "/{course_id}",
    summary="Deletar curso",
    description="Remove um curso específico do usuário autenticado.",
    response_model=ApiCompletedResponseSchema
)
def delete_course(
    course_id: str,
    x_token_login: str = Header(..., alias="X-Token-Login"),
    x_token_password: str = Header(..., alias="X-Token-Password")
):
    """
    Remove um curso do usuário.

    Args:
        course_id: Identificador do curso.
        x_token_login: Parte identificadora do token.
        x_token_password: Parte complementar do token.

    Returns:
        ApiCompletedResponseSchema: Resposta de conclusão.
    """
    return ApiCompletedResponseSchema(message="Completed")