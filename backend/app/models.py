# -*- coding: utf-8 -*-
"""ORM models para CIIU 4.0 (Python 3.8+ compatible)."""

from __future__ import annotations

try:
    from sqlalchemy import (
        Column, Integer, String, Text, SmallInteger, ForeignKey,
        DateTime, ARRAY, DECIMAL, CHAR, func,
    )
    from sqlalchemy.orm import relationship
except ImportError:
    raise SystemExit("Instala SQLAlchemy: pip install sqlalchemy psycopg2-binary")

from .database import Base


class Seccion(Base):
    __tablename__ = "secciones"
    id = Column(Integer, primary_key=True)
    codigo = Column(CHAR(1), nullable=False, unique=True, index=True)
    descripcion = Column(String(500), nullable=False)
    notas = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    divisiones = relationship("Division", back_populates="seccion", cascade="all, delete-orphan")


class Division(Base):
    __tablename__ = "divisiones"
    id = Column(Integer, primary_key=True)
    seccion_id = Column(Integer, ForeignKey("secciones.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo = Column(String(3), nullable=False, unique=True, index=True)
    codigo_numerico = Column(SmallInteger, nullable=False)
    descripcion = Column(String(500))
    notas = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    seccion = relationship("Seccion", back_populates="divisiones")
    grupos = relationship("Grupo", back_populates="division", cascade="all, delete-orphan")


class Grupo(Base):
    __tablename__ = "grupos"
    id = Column(Integer, primary_key=True)
    division_id = Column(Integer, ForeignKey("divisiones.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo = Column(String(4), nullable=False, unique=True, index=True)
    codigo_numerico = Column(SmallInteger, nullable=False)
    descripcion = Column(String(500))
    notas = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    division = relationship("Division", back_populates="grupos")
    clases = relationship("Clase", back_populates="grupo", cascade="all, delete-orphan")


class Clase(Base):
    __tablename__ = "clases"
    id = Column(Integer, primary_key=True)
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo = Column(String(5), nullable=False, unique=True, index=True)
    codigo_numerico = Column(SmallInteger, nullable=False)
    descripcion = Column(String(1000), nullable=False)
    notas_comprende = Column(Text)
    notas_adicionales = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    grupo = relationship("Grupo", back_populates="clases")
    subclases = relationship("Subclase", back_populates="clase", cascade="all, delete-orphan")
    actividades = relationship("Actividad", back_populates="clase", cascade="all, delete-orphan")
    exclusiones = relationship("Exclusion", back_populates="clase", cascade="all, delete-orphan")


class Subclase(Base):
    __tablename__ = "subclases"
    id = Column(Integer, primary_key=True)
    clase_id = Column(Integer, ForeignKey("clases.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo = Column(String(10), nullable=False, unique=True, index=True)
    codigo_numerico = Column(DECIMAL(5, 1), nullable=False)
    descripcion = Column(String(1000), nullable=False)
    notas = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    clase = relationship("Clase", back_populates="subclases")
    actividades = relationship("Actividad", back_populates="subclase")


class Actividad(Base):
    __tablename__ = "actividades"
    id = Column(Integer, primary_key=True)
    subclase_id = Column(Integer, ForeignKey("subclases.id", ondelete="SET NULL"), index=True)
    clase_id = Column(Integer, ForeignKey("clases.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo = Column(String(10), nullable=False, unique=True, index=True)
    codigo_numerico = Column(DECIMAL(6, 2), nullable=False)
    descripcion = Column(String(1500), nullable=False)
    descripcion_larga = Column(Text)
    palabras_clave = Column(ARRAY(Text))
    pagina_pdf = Column(SmallInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    subclase = relationship("Subclase", back_populates="actividades")
    clase = relationship("Clase", back_populates="actividades")


class Exclusion(Base):
    __tablename__ = "exclusiones"
    id = Column(Integer, primary_key=True)
    clase_id = Column(Integer, ForeignKey("clases.id", ondelete="CASCADE"), nullable=False, index=True)
    descripcion_texto = Column(Text, nullable=False)
    codigo_clase_destino = Column(String(10), index=True)
    descripcion_destino = Column(Text)
    pagina_pdf = Column(SmallInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    clase = relationship("Clase", back_populates="exclusiones")
