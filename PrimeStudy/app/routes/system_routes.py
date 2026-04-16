from fastapi import APIRouter


router = APIRouter(tags=["System"])


@router.get(
    "/",
    summary="Verificar status da API",
    description="Endpoint simples para confirmar que a API está em execução."
)
def health_check():
    """
    Retorna uma mensagem simples informando que a API está ativa.

    Returns:
        dict: Mensagem de confirmação.
    """
    return {"message": "API running."}