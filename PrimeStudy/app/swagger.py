from fastapi import FastAPI
import webbrowser
import threading

from app.routes.system_routes import router as system_router
from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.course_routes import router as course_router


def _open_browser():
    """
    Abre o Swagger no navegador padrão.

    Executado em uma thread separada para não travar a inicialização da API.
    """
    webbrowser.open("http://127.0.0.1:8000/docs")


def create_app() -> FastAPI:
    """
    Cria e configura a aplicação principal da API.

    Também configura a abertura automática do Swagger no navegador
    ao iniciar o servidor.

    Returns:
        FastAPI: Instância configurada da aplicação.
    """
    app = FastAPI(
        title="Academic User Courses API",
        description=(
            "API acadêmica para gerenciamento de usuários, autenticação "
            "por token temporário e organização de cursos e subtópicos."
        ),
        version="1.0.0"
    )

    # Registro das rotas
    app.include_router(system_router)
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(course_router)

    @app.on_event("startup")
    def startup_event():
        """
        Evento executado ao iniciar a API.

        Responsável por abrir automaticamente o Swagger no navegador.
        """
        threading.Timer(1.5, _open_browser).start()

    return app