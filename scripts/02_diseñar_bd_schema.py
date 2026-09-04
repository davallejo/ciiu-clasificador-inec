# -*- coding: utf-8 -*-
"""
PASO 0b: Genera database/schema.sql a partir del string SCHEMA_SQL.
(Opcional — el resultado es el mismo que database/schema.sql estático.)

Python 3.8+ compatible.
"""

from __future__ import print_function, unicode_literals

import os
import sys

SCHEMA_SQL = """
-- ============================================================
-- CIIU 4.0 - Esquema oficial INEC para PostgreSQL
-- ============================================================

DROP TABLE IF EXISTS exclusiones CASCADE;
DROP TABLE IF EXISTS actividades CASCADE;
DROP TABLE IF EXISTS subclases CASCADE;
DROP TABLE IF EXISTS clases CASCADE;
DROP TABLE IF EXISTS grupos CASCADE;
DROP TABLE IF EXISTS divisiones CASCADE;
DROP TABLE IF EXISTS secciones CASCADE;

CREATE TABLE secciones (
    id               SERIAL PRIMARY KEY,
    codigo           CHAR(1)      NOT NULL UNIQUE,
    descripcion      VARCHAR(500) NOT NULL,
    notas            TEXT,
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);

CREATE TABLE divisiones (
    id               SERIAL PRIMARY KEY,
    seccion_id       INTEGER      NOT NULL REFERENCES secciones(id) ON DELETE CASCADE,
    codigo           VARCHAR(3)   NOT NULL UNIQUE,
    codigo_numerico  SMALLINT     NOT NULL,
    descripcion      VARCHAR(500),
    notas            TEXT,
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_divisiones_seccion ON divisiones(seccion_id);

CREATE TABLE grupos (
    id               SERIAL PRIMARY KEY,
    division_id      INTEGER      NOT NULL REFERENCES divisiones(id) ON DELETE CASCADE,
    codigo           VARCHAR(4)   NOT NULL UNIQUE,
    codigo_numerico  SMALLINT     NOT NULL,
    descripcion      VARCHAR(500),
    notas            TEXT,
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_grupos_division ON grupos(division_id);

CREATE TABLE clases (
    id               SERIAL PRIMARY KEY,
    grupo_id         INTEGER      NOT NULL REFERENCES grupos(id) ON DELETE CASCADE,
    codigo           VARCHAR(5)   NOT NULL UNIQUE,
    codigo_numerico  SMALLINT     NOT NULL,
    descripcion      VARCHAR(1000) NOT NULL,
    notas_comprende  TEXT,
    notas_adicionales TEXT,
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_clases_grupo ON clases(grupo_id);

CREATE TABLE subclases (
    id               SERIAL PRIMARY KEY,
    clase_id         INTEGER      NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    codigo           VARCHAR(10)  NOT NULL UNIQUE,
    codigo_numerico  DECIMAL(5,1) NOT NULL,
    descripcion      VARCHAR(1000) NOT NULL,
    notas            TEXT,
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_subclases_clase ON subclases(clase_id);

CREATE TABLE actividades (
    id               SERIAL PRIMARY KEY,
    subclase_id      INTEGER      REFERENCES subclases(id) ON DELETE SET NULL,
    clase_id         INTEGER      NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    codigo           VARCHAR(10)  NOT NULL UNIQUE,
    codigo_numerico  DECIMAL(6,2) NOT NULL,
    descripcion      VARCHAR(1500) NOT NULL,
    descripcion_larga TEXT,
    palabras_clave   TEXT[],
    pagina_pdf       SMALLINT,
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_actividades_subclase ON actividades(subclase_id);
CREATE INDEX idx_actividades_clase   ON actividades(clase_id);
CREATE INDEX idx_actividades_codigo  ON actividades(codigo);
CREATE INDEX idx_actividades_fts ON actividades
USING GIN (to_tsvector('spanish', COALESCE(descripcion, '') || ' ' || COALESCE(descripcion_larga, '')));

CREATE TABLE exclusiones (
    id                    SERIAL PRIMARY KEY,
    clase_id              INTEGER      NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    descripcion_texto     TEXT         NOT NULL,
    codigo_clase_destino  VARCHAR(10),
    descripcion_destino   TEXT,
    pagina_pdf            SMALLINT,
    created_at            TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_exclusiones_clase ON exclusiones(clase_id);
CREATE INDEX idx_exclusiones_destino ON exclusiones(codigo_clase_destino);

CREATE OR REPLACE VIEW vw_actividad_completa AS
SELECT
    a.id              AS actividad_id,
    a.codigo          AS actividad_codigo,
    a.descripcion     AS actividad_descripcion,
    a.descripcion_larga AS actividad_descripcion_larga,
    a.palabras_clave  AS actividad_palabras_clave,
    s.codigo          AS seccion_codigo,
    s.descripcion     AS seccion_descripcion,
    d.codigo          AS division_codigo,
    d.descripcion     AS division_descripcion,
    g.codigo          AS grupo_codigo,
    g.descripcion     AS grupo_descripcion,
    c.codigo          AS clase_codigo,
    c.descripcion     AS clase_descripcion,
    sc.codigo         AS subclase_codigo,
    sc.descripcion    AS subclase_descripcion,
    a.pagina_pdf
FROM actividades a
JOIN clases  c  ON c.id  = a.clase_id
LEFT JOIN subclases sc ON sc.id = a.subclase_id
JOIN grupos  g  ON g.id  = c.grupo_id
JOIN divisiones d ON d.id = g.division_id
JOIN secciones s  ON s.id = d.seccion_id;

CREATE OR REPLACE VIEW vw_conteos_jerarquia AS
SELECT 'secciones'   AS nivel, COUNT(*) AS total FROM secciones   UNION ALL
SELECT 'divisiones',  COUNT(*) FROM divisiones  UNION ALL
SELECT 'grupos',      COUNT(*) FROM grupos      UNION ALL
SELECT 'clases',      COUNT(*) FROM clases      UNION ALL
SELECT 'subclases',   COUNT(*) FROM subclases   UNION ALL
SELECT 'actividades', COUNT(*) FROM actividades UNION ALL
SELECT 'exclusiones', COUNT(*) FROM exclusiones;
"""

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(BASE_DIR, "database", "schema.sql")
    if not os.path.isdir(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(SCHEMA_SQL)
    print("[OK] Schema SQL guardado en: %s" % out_path)
    print("     Aplícalo con:  python scripts/03_aplicar_schema.py")
