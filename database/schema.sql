
-- ============================================================
-- CIIU 4.0 - Esquema oficial INEC
-- ============================================================

-- Limpiar por si se ejecuta de nuevo (en orden correcto de FK)
DROP TABLE IF EXISTS exclusiones CASCADE;
DROP TABLE IF EXISTS actividades CASCADE;
DROP TABLE IF EXISTS subclases CASCADE;
DROP TABLE IF EXISTS clases CASCADE;
DROP TABLE IF EXISTS grupos CASCADE;
DROP TABLE IF EXISTS divisiones CASCADE;
DROP TABLE IF EXISTS secciones CASCADE;

-- ------------------------------------------------------------
-- NIVEL 1: SECCIONES (1 letra, 21 registros A-U)
-- ------------------------------------------------------------
CREATE TABLE secciones (
    id               SERIAL PRIMARY KEY,
    codigo           CHAR(1)      NOT NULL UNIQUE,
    descripcion      VARCHAR(500) NOT NULL,
    notas            TEXT,
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);

-- ------------------------------------------------------------
-- NIVEL 2: DIVISIONES (2 dígitos, ej. A01)
-- ------------------------------------------------------------
CREATE TABLE divisiones (
    id               SERIAL PRIMARY KEY,
    seccion_id       INTEGER      NOT NULL REFERENCES secciones(id) ON DELETE CASCADE,
    codigo           VARCHAR(3)   NOT NULL UNIQUE,          -- ej. A01
    codigo_numerico  SMALLINT     NOT NULL,                 -- ej. 1
    descripcion      VARCHAR(500),                         -- algunas divisiones no tienen título propio
    notas            TEXT,
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_divisiones_seccion ON divisiones(seccion_id);

-- ------------------------------------------------------------
-- NIVEL 3: GRUPOS (3 dígitos, ej. A011)
-- ------------------------------------------------------------
CREATE TABLE grupos (
    id               SERIAL PRIMARY KEY,
    division_id      INTEGER      NOT NULL REFERENCES divisiones(id) ON DELETE CASCADE,
    codigo           VARCHAR(4)   NOT NULL UNIQUE,          -- ej. A011
    codigo_numerico  SMALLINT     NOT NULL,                 -- ej. 11
    descripcion      VARCHAR(500),
    notas            TEXT,
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_grupos_division ON grupos(division_id);

-- ------------------------------------------------------------
-- NIVEL 4: CLASES (4 dígitos, ej. A0113) - 417 registros aprox.
-- ------------------------------------------------------------
CREATE TABLE clases (
    id               SERIAL PRIMARY KEY,
    grupo_id         INTEGER      NOT NULL REFERENCES grupos(id) ON DELETE CASCADE,
    codigo           VARCHAR(5)   NOT NULL UNIQUE,          -- ej. A0113
    codigo_numerico  SMALLINT     NOT NULL,                 -- ej. 113
    descripcion      VARCHAR(1000) NOT NULL,
    notas_comprende  TEXT,                                 -- "ESTA CLASE COMPRENDE:"
    notas_adicionales TEXT,                                -- notas/observaciones varias
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_clases_grupo ON clases(grupo_id);

-- ------------------------------------------------------------
-- NIVEL 5: SUBCLASES (4 díg + .N, ej. A0113.2)
-- ------------------------------------------------------------
CREATE TABLE subclases (
    id               SERIAL PRIMARY KEY,
    clase_id         INTEGER      NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    codigo           VARCHAR(10)  NOT NULL UNIQUE,          -- ej. A0113.2
    codigo_numerico  DECIMAL(5,1) NOT NULL,                 -- ej. 113.2
    descripcion      VARCHAR(1000) NOT NULL,
    notas            TEXT,
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_subclases_clase ON subclases(clase_id);

-- ------------------------------------------------------------
-- NIVEL 6: ACTIVIDADES DETALLADAS (4 díg + .NN, ej. A0113.22)
--          ~1,724 registros - NIVEL OBJETIVO DEL MODELO DE IA
-- ------------------------------------------------------------
CREATE TABLE actividades (
    id               SERIAL PRIMARY KEY,
    subclase_id      INTEGER      REFERENCES subclases(id) ON DELETE SET NULL,
    clase_id         INTEGER      NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    codigo           VARCHAR(10)  NOT NULL UNIQUE,          -- ej. A0113.22
    codigo_numerico  DECIMAL(6,2) NOT NULL,                 -- ej. 113.22
    descripcion      VARCHAR(1500) NOT NULL,                -- descripción corta (el título)
    descripcion_larga TEXT,                                 -- descripción extendida si existe
    palabras_clave   TEXT[],                                 -- array de keywords extraídos
    pagina_pdf       SMALLINT,                               -- trazabilidad: página de origen
    created_at       TIMESTAMPTZ  DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_actividades_subclase ON actividades(subclase_id);
CREATE INDEX idx_actividades_clase   ON actividades(clase_id);
CREATE INDEX idx_actividades_codigo  ON actividades(codigo);

-- Índice FULL TEXT para búsquedas semánticas rápidas
CREATE INDEX idx_actividades_fts ON actividades
USING GIN (to_tsvector('spanish', COALESCE(descripcion, '') || ' ' || COALESCE(descripcion_larga, '')));

-- ------------------------------------------------------------
-- TABLA DE EXCLUSIONES / REFERENCIAS CRUZADAS
-- Almacena los bloques "ESTA CLASE NO COMPRENDE:"
-- Estos NO son actividades reales; son pointers que dicen
-- "esta descripción X NO pertenece a la clase Y, pertenece a la clase Z".
-- ~388 registros.
-- ------------------------------------------------------------
CREATE TABLE exclusiones (
    id                    SERIAL PRIMARY KEY,
    clase_id              INTEGER      NOT NULL REFERENCES clases(id) ON DELETE CASCADE,
    descripcion_texto     TEXT         NOT NULL,            -- el texto que NO va aquí
    codigo_clase_destino  VARCHAR(10),                      -- la clase donde SÍ va (ej. B0892)
    descripcion_destino   TEXT,                             -- título de la clase destino (para trazabilidad)
    pagina_pdf            SMALLINT,
    created_at            TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX idx_exclusiones_clase ON exclusiones(clase_id);
CREATE INDEX idx_exclusiones_destino ON exclusiones(codigo_clase_destino);

-- ============================================================
-- VISTAS UTILES
-- ============================================================

-- Vista que une toda la jerarquía de una actividad detallada
-- (para entrenar el modelo de IA con todo el contexto)
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

-- Vista conteos por nivel (para validar carga correcta)
CREATE OR REPLACE VIEW vw_conteos_jerarquia AS
SELECT
    'secciones'   AS nivel, COUNT(*) AS total FROM secciones
UNION ALL
SELECT 'divisiones',  COUNT(*) FROM divisiones
UNION ALL
SELECT 'grupos',      COUNT(*) FROM grupos
UNION ALL
SELECT 'clases',      COUNT(*) FROM clases
UNION ALL
SELECT 'subclases',   COUNT(*) FROM subclases
UNION ALL
SELECT 'actividades', COUNT(*) FROM actividades
UNION ALL
SELECT 'exclusiones', COUNT(*) FROM exclusiones;
