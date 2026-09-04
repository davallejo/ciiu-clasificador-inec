# -*- coding: utf-8 -*-
"""Pydantic schemas para la API (Python 3.8+ compatible).

Compatible con Pydantic v1 y v2:
  - v2: usa `model_config = ConfigDict(from_attributes=True)`
  - v1: usa `class Config: orm_mode = True`
"""

from __future__ import annotations

from typing import List, Optional

try:
    from pydantic import BaseModel, ConfigDict
    _PYDANTIC_V2 = True
except ImportError:
    _PYDANTIC_V2 = False
    from pydantic import BaseModel  # type: ignore
    class ConfigDict(dict):  # type: ignore
        pass


# -------- Helper: factoría para los esquemas ORM-compatibles --------
if _PYDANTIC_V2:
    _SeccionBase = BaseModel
    _DivisionBase = BaseModel
    _GrupoBase = BaseModel
    _ClaseBase = BaseModel
    _SubclaseBase = BaseModel
    _ActividadBase = BaseModel
    _ExclusionBase = BaseModel

    class SeccionOut(_SeccionBase):
        model_config = ConfigDict(from_attributes=True)
        codigo: str
        descripcion: str

    class DivisionOut(_DivisionBase):
        model_config = ConfigDict(from_attributes=True)
        codigo: str
        descripcion: Optional[str] = None

    class GrupoOut(_GrupoBase):
        model_config = ConfigDict(from_attributes=True)
        codigo: str
        descripcion: Optional[str] = None

    class ClaseOut(_ClaseBase):
        model_config = ConfigDict(from_attributes=True)
        codigo: str
        descripcion: str
        notas_comprende: Optional[str] = None

    class SubclaseOut(_SubclaseBase):
        model_config = ConfigDict(from_attributes=True)
        codigo: str
        descripcion: str

    class ActividadOut(_ActividadBase):
        model_config = ConfigDict(from_attributes=True)
        codigo: str
        descripcion: str
        descripcion_larga: Optional[str] = None
        pagina_pdf: Optional[int] = None

    class ExclusionOut(_ExclusionBase):
        model_config = ConfigDict(from_attributes=True)
        clase_codigo: Optional[str] = None
        descripcion_texto: str
        codigo_clase_destino: Optional[str] = None
        descripcion_destino: Optional[str] = None
        pagina_pdf: Optional[int] = None
else:
    class _OrmConfig(object):
        orm_mode = True

    class SeccionOut(BaseModel):  # type: ignore
        Config = _OrmConfig
        codigo: str
        descripcion: str

    class DivisionOut(BaseModel):  # type: ignore
        Config = _OrmConfig
        codigo: str
        descripcion: Optional[str] = None

    class GrupoOut(BaseModel):  # type: ignore
        Config = _OrmConfig
        codigo: str
        descripcion: Optional[str] = None

    class ClaseOut(BaseModel):  # type: ignore
        Config = _OrmConfig
        codigo: str
        descripcion: str
        notas_comprende: Optional[str] = None

    class SubclaseOut(BaseModel):  # type: ignore
        Config = _OrmConfig
        codigo: str
        descripcion: str

    class ActividadOut(BaseModel):  # type: ignore
        Config = _OrmConfig
        codigo: str
        descripcion: str
        descripcion_larga: Optional[str] = None
        pagina_pdf: Optional[int] = None

    class ExclusionOut(BaseModel):  # type: ignore
        Config = _OrmConfig
        clase_codigo: Optional[str] = None
        descripcion_texto: str
        codigo_clase_destino: Optional[str] = None
        descripcion_destino: Optional[str] = None
        pagina_pdf: Optional[int] = None


# -------- Predicción --------
class PrediccionItem(BaseModel):
    score: float
    score_porcentaje: float
    actividad_codigo: str
    actividad_descripcion: str

    clase_codigo: str
    clase_descripcion: str

    subclase_codigo: Optional[str] = None
    subclase_descripcion: Optional[str] = None

    grupo_codigo: str
    grupo_descripcion: Optional[str] = None

    division_codigo: str
    division_descripcion: Optional[str] = None

    seccion_codigo: str
    seccion_descripcion: str

    pagina_pdf: Optional[int] = None


class PredictRequest(BaseModel):
    texto: str
    top_k: int = 5
    umbral_minimo: float = 0.0


class PredictResponse(BaseModel):
    texto_ingresado: str
    total_coincidencias: int
    resultados: List[PrediccionItem]
    modelo_usado: str
    tiempo_ms: float
    advertencia: Optional[str] = None


# -------- Health --------
class HealthResponse(BaseModel):
    status: str = "ok"
    ambiente: str
    actividades_cargadas: int = 0
    modelo_entrenado: bool = False
