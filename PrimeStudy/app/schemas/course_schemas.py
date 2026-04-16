from typing import Optional
from pydantic import BaseModel, Field


class CourseCreateRequestSchema(BaseModel):
    """
    Modelo de entrada para criação de curso.
    """

    name: str = Field(..., description="Nome do curso.")
    last_topic: Optional[str] = Field(None, description="Último tópico estudado.")
    parent_id: Optional[str] = Field(
        None,
        description="Identificador do curso pai. Se informado, cria o curso como subtópico."
    )


class CourseUpdateRequestSchema(BaseModel):
    """
    Modelo de entrada para atualização rápida de curso.
    """

    new_name: Optional[str] = Field(None, description="Novo nome do curso.")
    new_last_topic: Optional[str] = Field(None, description="Novo último tópico estudado.")


class CourseResponseSchema(BaseModel):
    """
    Modelo de saída contendo dados de um curso.
    """

    uuid: str = Field(..., description="Identificador único do curso.")
    name: str = Field(..., description="Nome do curso.")
    last_topic: str = Field(..., description="Último tópico estudado.")
    subtopics_count: int = Field(..., description="Quantidade de subtópicos vinculados.")