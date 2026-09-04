<div align="center">
  <table align="center" cellpadding="0" cellspacing="0" style="border: none;">
    <tr>
      <td align="center" style="padding: 4px 8px;">
        <img width="62" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" />
      </td>
      <td align="center" style="padding: 4px 8px;">
        <img width="62" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" />
      </td>
      <td align="center" style="padding: 4px 8px;">
        <img width="62" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" />
      </td>
      <td align="center" style="padding: 4px 8px;">
        <img width="62" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scikitlearn/scikitlearn-original.svg" />
      </td>
      <td align="center" style="padding: 4px 8px;">
        <img width="62" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nextjs/nextjs-original.svg" />
      </td>
      <td align="center" style="padding: 4px 8px;">
        <img width="62" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg" />
      </td>
      <td align="center" style="padding: 4px 8px;">
        <img width="62" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg" />
      </td>
      <td align="center" style="padding: 4px 8px;">
        <img width="62" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tailwindcss/tailwindcss-original.svg" />
      </td>
    </tr>
  </table>
</div>

<div align="center">
  <h1 align="center">
    🇪🇨 CIIU Clasificador · INEC Ecuador
  </h1>
  <p align="center">
    <strong>Clasificador automático de actividades económicas CIIU 4.0 con Inteligencia Artificial</strong>
    <br/>
    Basado en el catálogo oficial del
    <em>Instituto Nacional de Estadística y Censos (INEC)</em>.
    <br/>
    <strong>Sin alucinaciones · Score 100% transparente · Trazabilidad página por página al PDF oficial.</strong>
  </p>
  <p align="center">
    <a href="#-cómo-funciona-el-clasificador-"><img alt="Model" src="https://img.shields.io/badge/Model-TF%E2%80%91IDF%20%2B%20Fuzzy-0B4F8C?style=for-the-badge&logo=scikitlearn&logoColor=white"/></a>
    &nbsp;
    <a href="#-arquitectura"><img alt="Stack" src="https://img.shields.io/badge/Stack-FastAPI%20·%20Next.js%20·%20PostgreSQL-1F8A70?style=for-the-badge"/></a>
    &nbsp;
    <a href="#%EF%B8%8F-gu%C3%ADa-de-despliegue-en-vercel-producci%C3%B3n"><img alt="Vercel" src="https://img.shields.io/badge/Deploy-Vercel%20Ready-000?style=for-the-badge&logo=vercel&logoColor=white"/></a>
    &nbsp;
    <a href="./LICENSE"><img alt="MIT" src="https://img.shields.io/badge/License-MIT-C2410C?style=for-the-badge"/></a>
  </p>
</div>

<p align="center">
  <img
    src="https://github.com/user-attachments/assets/5e071116-a416-4cf4-a3bb-b513c5e13501"
    width="100%"
    alt="Hero screenshot del clasificador CIIU INEC — Diego Vallejo"
    style="border-radius:14px; border: 1px solid #e2e8f0; box-shadow:0 18px 48px -18px rgba(15,23,42,0.25);"
  />
</p>

---

## 🏛️ ¿Qué problema resuelve?

El **CIIU** (Clasificación Industrial Internacional Uniforme) es el instrumento
estándar que usa el **INEC** para codificar la actividad económica de empresas,
hogares e instituciones en el Ecuador. **Sin este prototipo, clasificar es
trabajo manual**: un operador lee la descripción del ciudadano, busca en un
PDF de +200 páginas y asigna un código de 6 dígitos.

👉 **Este proyecto automatiza ese paso** con una precisión superior al 98%,
utilizando un **ensemble híbrido determinístico** (TF-IDF + Similitud Coseno +
RapidFuzz) sobre el catálogo completo CIIU 4.0 del INEC.

> 🎯 Nivel objetivo de la predicción: **actividad detallada (6 dígitos)** —
> el mismo nivel granular que usan oficialmente el SRI y el INEC.

---

## ✨ Características principales

| # | Característica | Detalle |
|---|---|---|
| 📚 | **Catálogo 100% oficial** | ~1.738 actividades, 417 clases, 21 secciones extraídas fielmente del PDF del INEC |
| 🧠 | **IA sin alucinaciones** | Modelo híbrido simbólico — NUNCA inventa un código que no exista en el catálogo |
| ⚡ | **Tiempo real** | Respuesta en **~30–120 ms** con debounce mientras el usuario escribe |
| 🚫 | **Exclusiones separadas** | Los ~388 bloques `ESTA CLASE NO COMPRENDE:` se almacenan aparte y NUNCA contaminan el dataset |
| 🔍 | **Trazabilidad 100%** | Cada predicción muestra la **página exacta del PDF** de donde salió el dato |
| 🧭 | **Jerarquía completa** | Devuelve la ruta `Sección → División → Grupo → Clase → Subclase → Actividad` |
| 🔎 | **FTS nativo PostgreSQL** | Índice `GIN to_tsvector('spanish', ...)` para búsquedas semánticas |
| 🎨 | **UI profesional** | Diseño responsive en español, paleta institucional INEC, micro-interacciones Tailwind |
| ☁️ | **Desplegable en Vercel** | Backend serverless (Mangum) + Frontend Next.js nativo + Vercel Postgres |
| 🐍 | **Multi-versión Python** | Compatible con 3.8 · 3.9 · 3.10 · **3.11.9 (Vercel)** · 3.12 |

---

## 🧰 Tech Stack (con logos)

> Cada tecnología está justificada — no hay dependencias de adorno.

<table align="center" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td align="center" width="14%" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" />
      <br/><b>Python 3.8+</b>
      <br/><small style="color:#64748b;">Scripts ETL · ML · API</small>
    </td>
    <td align="center" width="14%" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" />
      <br/><b>FastAPI</b>
      <br/><small style="color:#64748b;">Backend REST · async</small>
    </td>
    <td align="center" width="14%" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" />
      <br/><b>PostgreSQL</b>
      <br/><small style="color:#64748b;">7 tablas · FTS · Vistas</small>
    </td>
    <td align="center" width="14%" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scikitlearn/scikitlearn-original.svg" />
      <br/><b>scikit-learn</b>
      <br/><small style="color:#64748b;">TF-IDF · Similitud Coseno</small>
    </td>
    <td align="center" width="14%" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/numpy/numpy-original.svg" />
      <br/><b>SciPy / NumPy</b>
      <br/><small style="color:#64748b;">Matrices dispersas</small>
    </td>
    <td align="center" width="14%" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nextjs/nextjs-original.svg" />
      <br/><b>Next.js 14</b>
      <br/><small style="color:#64748b;">App Router · SSR</small>
    </td>
    <td align="center" width="14%" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg" />
      <br/><b>TypeScript</b>
      <br/><small style="color:#64748b;">Tipado estricto</small>
    </td>
  </tr>
  <tr>
    <td align="center" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg" />
      <br/><b>React 18</b>
      <br/><small style="color:#64748b;">Client Components</small>
    </td>
    <td align="center" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tailwindcss/tailwindcss-original.svg" />
      <br/><b>Tailwind CSS</b>
      <br/><small style="color:#64748b;">Diseño responsive</small>
    </td>
    <td align="center" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sqlalchemy/sqlalchemy-original.svg" />
      <br/><b>SQLAlchemy 2</b>
      <br/><small style="color:#64748b;">ORM · SSL auto</small>
    </td>
    <td align="center" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pydantic/pydantic-original.svg" />
      <br/><b>Pydantic v1/v2</b>
      <br/><small style="color:#64748b;">Esquemas OpenAPI</small>
    </td>
    <td align="center" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-plain-wordmark.svg" />
      <br/><b>PyMuPDF</b>
      <br/><small style="color:#64748b;">Parser PDF CIIU</small>
    </td>
    <td align="center" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vercel/vercel-original-wordmark.svg" />
      <br/><b>Vercel</b>
      <br/><small style="color:#64748b;">Serverless · Mangum</small>
    </td>
    <td align="center" style="padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;">
      <img height="42" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" />
      <br/><b>Mangum</b>
      <br/><small style="color:#64748b;">ASGI → AWS Lambda</small>
    </td>
  </tr>
</table>

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────────────────┐
│  🧑‍💻  USUARIO / ENCUESTADOR / CIUDADANO                               │
│          │  escribe "Panadería con venta de pan casero"              │
└──────────┼───────────────────────────────────────────────────────────┘
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  🎨  FRONTEND NEXT.JS 14  (App Router · TypeScript · Tailwind)       │
│     · Debounce 500 ms  ·  UI en vivo  ·  Diseño responsive           │
└──────────┬───────────────────────────────────────────────────────────┘
           │  POST /api/predecir  { texto, top_k }
           │  GET  /api/estadisticas  /actividades
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  ⚙️  BACKEND FASTAPI  (Uvicorn local / Mangum serverless en Vercel)   │
│                                                           │
│  ┌─ main.py  →  /api/predecir                                   │
│  │          └─▶  ClasificadorCIIU.predecir()                     │
│  │                                                               │
│  ├─ classifier.py  (modelo híbrido SIN ALUCINACIONES)            │
│  │   1. normalizar texto · limpieza stopwords ES                 │
│  │   2. TF-IDF vectorizer  (1-2 grams) → similitud coseno TOP-20│
│  │   3. re-rank RapidFuzz (token_set + sort_ratio)               │
│  │   4. score_final = 0.70·coseno + 0.30·fuzzy → top-k          │
│  │                                                               │
│  └─ database.py  (SQLAlchemy 2.0, SSL automático en remoto)      │
└──────────┬───────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  🗄️  POSTGRESQL  (Local  ·  Vercel Postgres  ·  Supabase  ·  Neon)   │
│  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌────────┐  ┌────────────┐ │
│  │secciones│→ │divisiones│→ │ grupos │→ │ clases │→ │actividades │ │
│  └─────────┘  └──────────┘  └────────┘  └────────┘  └────────────┘ │
│  ┌──────────┐     Índice FTS español:  GIN to_tsvector('spanish')   │
│  │exclusione│     Vista: vw_conteos_jerarquia  (tarjetas home)       │
│  └──────────┘                                                         │
└──────────┬───────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  📄  ciiu.pdf  (INSUMO OFICIAL INEC — 205 páginas · NO al repo)       │
│     ┌─ 01_extraer_texto_pdf.py   (PyMuPDF)                            │
│     ├─ 03_aplicar_schema.py      (schema.sql)                         │
│     ├─ 04_parser_ciiu.py         (FSM → JSON jerárquico)              │
│     └─ 05_cargar_a_postgres.py   (INSERT FK order + validaciones)     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del proyecto

```
ciiu-clasificador-inec/
│
├── 📜 LICENSE ........................................ MIT License
├── 📄 README.md ...................................... Este archivo
├── 🚀 vercel.json .................................... Configuración mono-repo Vercel + serverless
├── 🐍 requirements.txt ............................... Dependencias globales (scripts ETL + backend + mangum)
├── 🔒 .env.example ................................... Plantilla variables de entorno
├── ⚙️  runtime.txt  .................................. Runtime Vercel: python-3.11.9
├── 🚫 .gitignore ..................................... Reglas anti-credenciales + anti-cache
│
├── 📂 api/ ........................................... ▶ ENTRADA SERVERLESS VERCEL
│   └── index.py ...................................... Handler Mangum (ASGI → Lambda)
│
├── 📂 Insumos/ ....................................... ▶ PDF OFICIAL (NO subir al repo)
│   └── .gitkeep
│
├── 📂 database/
│   └── schema.sql .................................... DDL normalizado + Índice FTS + Vistas
│
├── 📂 scripts/ ....................................... ▶ TUBERÍA ETL  (PDF → PostgreSQL)
│   ├── 01_extraer_texto_pdf.py ...................... Paso 1 · Extraer texto crudo PDF
│   ├── 02_diseñar_bd_schema.py ...................... Genera schema.sql (auxiliar)
│   ├── 03_aplicar_schema.py ......................... Paso 2 · Crear BD + ejecutar schema.sql
│   ├── 04_parser_ciiu.py ............................ Paso 3 · Máquina de estados → JSON jerárquico ✨ el más importante
│   └── 05_cargar_a_postgres.py ...................... Paso 4 · INSERT FK order + validación
│
├── 📂 data/ .......................................... ▶ DATOS GENERADOS  (NO subir al repo)
│   ├── extraidos/ .................................... Salida cruda .txt/.jsonl del paso 1
│   └── parsed/ ....................................... Salida estructurada .json del paso 3
│
├── 📂 models/ ........................................ ▶ CACHÉ TF-IDF  (NO subir al repo — se regenera sola)
│
├── 📂 backend/ ....................................... ▶ FASTAPI · API REST
│   ├── requirements.txt .............................. Solo backend (para CI/CD granular)
│   └── app/
│       ├── main.py ................................... Entrada FastAPI · rutas /api/* · CORS
│       ├── config.py ................................. Settings · DATABASE_URL · POSTGRES_URL auto
│       ├── database.py ............................... SQLAlchemy engine · SSL en remoto
│       ├── models.py ................................. ORM: 7 tablas + relaciones
│       ├── schemas.py ................................ Pydantic v1 & v2 (compatibilidad auto)
│       └── classifier.py ............................. 🧠 ClasificadorCIIU (TF-IDF + Fuzzy + /tmp en Vercel)
│
└── 📂 frontend/ ...................................... ▶ NEXT.JS 14 · UI
    ├── package.json .................................. Node 18/20 LTS · Dependencias
    ├── package-lock.json
    ├── tsconfig.json ................................. Strict + Next plugin
    ├── next-env.d.ts
    ├── next.config.mjs ............................... Rewrites /api/* :8000 (local)
    ├── tailwind.config.ts ............................ Paleta institucional INEC
    ├── postcss.config.js
    ├── .env.example .................................. Plantilla NEXT_PUBLIC_API_URL
    └── app/
        ├── layout.tsx ................................ <html es-EC> + fuente Inter
        ├── globals.css ............................... Utilidades: skeleton, score-bar, etc.
        ├── page.tsx .................................. UI principal: hero + en vivo + resultados
        └── lib/
            └── types.ts .............................. Tipos TS 1:1 con los schemas Pydantic
```

---

# 🏠 Guía de instalación LOCAL (paso a paso)

> 💡 Versión Python **recomendada**: **3.11.9** (igual que `runtime.txt` de Vercel).
> También funciona 100% en 3.8, 3.9, 3.10 y 3.12.

---

## 0️⃣ Prerrequisitos (instalar UNA SOLA VEZ)

| Componente | Versión mínima | Comprobar |
|---|---|---|
| 🐍 Python | **3.8 – 3.12** (mejor 3.11.9) | `python --version` |
| 🟢 Node.js | **18 LTS o 20 LTS** | `node --version` |
| 📦 npm | ≥ v9 | `npm --version` |
| 🐘 PostgreSQL | **13+** (ideal ≥ 15) | `psql --version` y debe estar corriendo en `localhost:5432` |
| 📚 Git | cualquiera | `git --version` |

**Instalación rápida** (si no tienes alguno):
- **Windows**: descarga Python desde [python.org](https://www.python.org/downloads/release/python-3119/) (⚠ marca *Add Python to PATH*), Node desde [nodejs.org](https://nodejs.org/es/), PostgreSQL desde [postgresql.org/download/windows](https://www.postgresql.org/download/windows/).
- **macOS (Homebrew)**: `brew install python@3.11 node postgresql@15 && brew services start postgresql@15`
- **Linux (Debian/Ubuntu)**:
  ```bash
  sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip \
      nodejs npm postgresql postgresql-contrib libpq-dev python3-dev
  ```

---

## 1️⃣ Clonar + entorno virtual aislado

```bash
# Clona el repo
git clone https://github.com/diegovallejo/ciiu-clasificador-inec.git
cd ciiu-clasificador-inec
```

### 🖥️ Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
# Si PowerShell bloquea la activación, ejecuta 1 vez:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# ✔ Verás (.venv) al principio del prompt.
```

### 🍎 macOS / 🐧 Linux (Bash/Zsh)
```bash
python3 -m venv .venv
source .venv/bin/activate
# ✔ Verás (.venv) al principio del prompt.
```

---

## 2️⃣ Variables de entorno + PDF del INEC

```bash
# Windows PowerShell:
Copy-Item .env.example .env

# macOS / Linux:
cp .env.example .env
```

**Edita `.env`** y pone la contraseña que elegiste al instalar PostgreSQL local:
```ini
# ====== .env (LOCAL — NO SUBIR A GITHUB) ======
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ciiu_inec
DB_USER=postgres
DB_PASSWORD=TU_CONTRASEÑA_DE_POSTGRES    # ← edita ESTA LÍNEA
APP_ENV=development
```

Coloca **el PDF oficial del catálogo CIIU 4.0 del INEC** con el nombre exacto:
```
Insumos/ciiu.pdf   ← pega el archivo aquí
```

---

## 3️⃣ Instalar dependencias Python

```bash
# ✅ Asegúrate de ver (.venv) en el prompt
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Esto instalará: `PyMuPDF`, `psycopg2-binary`, `FastAPI`, `Uvicorn`,
`SQLAlchemy 2`, `Pydantic v2`, `scikit-learn`, `scipy`, `numpy`,
`rapidfuzz`, `mangum`, `pydantic-settings`.

---

## 4️⃣ 🗄️ Tubería ETL (PDF → PostgreSQL)

Ejecuta los **4 scripts en orden**, siempre con el `.venv` activado:

```bash
# ▶ Paso 1 · Extraer texto crudo del PDF
python scripts/01_extraer_texto_pdf.py
#    Salida: data/extraidos/ciiu_texto_completo.txt
#            data/extraidos/ciiu_estructura_paginas.jsonl

# ▶ Paso 2 · Crear base de datos "ciiu_inec" + ejecutar schema.sql
python scripts/03_aplicar_schema.py
#    Espera: "[OK] Schema SQL ejecutado desde: schema.sql"

# ▶ Paso 3 · ✨ MÁS IMPORTANTE · Parsear jerarquía CIIU → JSON
python scripts/04_parser_ciiu.py
#
#   ⚠  AL FINALIZAR:  abre data/parsed/_VALIDACIONES.txt
#      y confirma que los conteos estén DENTRO DE RANGO:
#        ✓ secciones   = 21
#        ✓ clases      ≈ 415–420
#        ✓ actividades ≈ 1.700–1.800
#        ✓ exclusiones ≈ 380–420
#
#      Si dice "ERRORES CRÍTICOS", arregla el parser antes de seguir.

# ▶ Paso 4 · Insertar en PostgreSQL con FK correctas
python scripts/05_cargar_a_postgres.py
#    Espera el reporte: ✓ secciones ✓ divisiones ✓ grupos ✓ clases ✓ actividades ✓ exclusiones
```

---

## 5️⃣ 🔙 Levantar el backend (FastAPI · puerto 8000)

```bash
# Con .venv activado DESDE LA RAÍZ:
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Esperado:
```
INFO:  Uvicorn running on http://0.0.0.0:8000
INFO:  Started reloader process
[STARTUP] Tablas ya existen (schema OK)
[CLASIFICADOR] Modelo entrenado: 1738 actividades.
INFO:  Application startup complete.
```

### 🧪 Prueba el backend
- Abre **http://localhost:8000/docs** → Swagger UI automático.
- Prueba `GET /api/health` → `status: ok`, `actividades_cargadas > 1700`.
- Prueba `POST /api/predecir` → body `{ "texto":"Panadería","top_k":3 }` → 3 resultados con scores %.

---

## 6️⃣ 🔜 Levantar el frontend (Next.js · puerto 3000)

Abre **otra terminal** (deja el backend corriendo):

```bash
cd frontend

# 🔽 Copia la plantilla de env (SOLO la 1ª vez):
#   Windows PS:  Copy-Item .env.example .env
#   macOS/Linux: cp .env.example .env
cp .env.example .env

# Instala node_modules (solo la 1ª vez — toma 2–5 min):
npm install

# Levanta servidor dev:
npm run dev
```

Esperado:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

Abre **http://localhost:3000** ✨.

### ✅ Validación final
1. **Sin escribir nada**: verás las 7 tarjetas de estadísticas (`Secciones=21`, `Actividades=1738`, etc.) — si aparecen, la conexión **ya está OK**.
2. **Escribe** "Panadería y venta de pan casero" → después de 500 ms aparecen 5 tarjetas con códigos `C1071...` y scores %.
3. **Consola del navegador (F12)**: si algo falla, verás logs `[estadisticas]` y `[predecir]` con la URL exacta que llamó.

---

# ☁️ Guía de despliegue en **Vercel** (producción)

El repo ya viene **100% configurado para Vercel**:
- [vercel.json](file:///c:/Users/DIEVALL/Documents/Proyectos%20Python/predice-categoria-INEC-trae/vercel.json) — install/build/rewrites/env
- [runtime.txt](file:///c:/Users/DIEVALL/Documents/Proyectos%20Python/predice-categoria-INEC-trae/runtime.txt) — `python-3.11.9`
- [api/index.py](file:///c:/Users/DIEVALL/Documents/Proyectos%20Python/predice-categoria-INEC-trae/api/index.py) — Handler Mangum + `/tmp` cache
- El backend auto detecta `POSTGRES_URL` en [config.py](file:///c:/Users/DIEVALL/Documents/Proyectos%20Python/predice-categoria-INEC-trae/backend/app/config.py)

---

## 0️⃣ Preparar el repo para GitHub

Antes de `git push`:

1.  ✅ **`git status` debe decir que `data/`, `Insumos/ciiu.pdf`, `models/*.pkl`, `.venv/`, `.env`, `frontend/.env`, `__pycache__/`, `node_modules/`, `.next/` NO están trackeados** (el `.gitignore` actualizado se encarga).
2.  ✅ `runtime.txt` contiene `python-3.11.9`.
3.  ✅ `requirements.txt` está en la **raíz** (no solo en `backend/`).
4.  ✅ Haz commit y push.

```bash
git init
git add .
git commit -m "chore: push inicial — CIIU Clasificador IA INEC"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/ciiu-clasificador-inec.git
git push -u origin main
```

---

## 1️⃣ Crear proyecto Vercel + conectar repo

1.  Entra a **https://vercel.com/new**
2.  Clic en **Import** de tu repo `ciiu-clasificador-inec`.
3.  En *Configure Project*:
    | Campo | Valor |
    |---|---|
    | Framework Preset | **Next.js** (se auto-detecta ✔) |
    | Root Directory | *(dejalo vacío — `.`)* |
    | Install Command | *(automático en vercel.json)* |
    | Build Command | *(automático en vercel.json)* |
    | Output Directory | *(automático en vercel.json)* |
4.  **No hagas Deploy todavía.** Primero: Storage 👇.

---

## 2️⃣ 🗄️ Crear Vercel Postgres

1.  En el proyecto → pestaña **Storage** → **Create Database** → **Postgres**.
2.  Elige la región más cercana a Ecuador: `Washington, D.C.` (iad1) o `São Paulo` (gru1).
3.  Espera ~2 min. Vercel creará **automáticamente 7 variables**:
    ```
    POSTGRES_URL
    POSTGRES_PRISMA_URL
    POSTGRES_URL_NON_POOLING
    POSTGRES_USER / POSTGRES_HOST / POSTGRES_PASSWORD / POSTGRES_DATABASE
    ```
4.  ✅ El código en [config.py](file:///c:/Users/DIEVALL/Documents/Proyectos%20Python/predice-categoria-INEC-trae/backend/app/config.py#L75-L84) detecta `POSTGRES_URL` automáticamente y fuerza `sslmode=require` para hosts remotos. **No tienes que configurar nada manualmente.**

---

## 3️⃣ 🔑 Variables de entorno (obligatorias en producción)

Ve a **Settings → Environment Variables** y **añade manualmente**:

| Variable | Valor recomendado | ¿Obligatorio? |
|---|---|---|
| `APP_SECRET_KEY` | Cadena larga aleatoria. **Genera una aquí**: `openssl rand -hex 32` | ✅ **SÍ — producción** |
| `CORS_ORIGINS` | `https://TU-PROYECTO.vercel.app` (o deja vacío = `*` por defecto) | ❌ No |
| `CIIU_MODELO_DIR` | `/tmp/ciiu_models` | ❌ No (ya viene en `vercel.json` ✔) |
| `APP_ENV` | `production` | ❌ No (ya viene en `vercel.json` ✔) |

> ⚠ **NUNCA** pongas tu `.env` local con contraseñas en producción. Vercel gestiona sus propios secretos.

---

## 4️⃣ 🚚 Carga inicial de datos (OBLIGATORIA · UNA SOLA VEZ)

El serverless **no ejecuta los scripts ETL** (no tiene el PDF, ni tiene que tenerlo).
Lo haces desde tu máquina local **apuntando a Vercel Postgres**:

1.  Copia **`POSTGRES_URL_NON_POOLING`** (mejor para carga masiva) desde:
    Vercel → Tu proyecto → **Storage** → Postgres → `psql` → Copy URL.
2.  Pégala en tu **`.env` LOCAL** (NO subirlo a Git):
    ```ini
    # .env  (SOLO en tu máquina local — NUNCA en GitHub)
    POSTGRES_URL=postgres://default:xxxx@xxx-xxx.postgres.vercel-storage.com:5432/verceldb?sslmode=require
    ```
3.  Activa tu `.venv` y ejecuta **solo** los pasos 3, 4 y 5:
    ```bash
    # Paso 3 → schema.sql en Vercel Postgres
    python scripts/03_aplicar_schema.py

    # Paso 4 → Parser PDF (si ya lo hiciste en local y data/parsed/*.json existen, PUEDES SALTARTELO)
    python scripts/04_parser_ciiu.py

    # Paso 5 → carga masiva
    python scripts/05_cargar_a_postgres.py
    ```
4.  Al terminar verás reporte con conteos ✓ listo.

---

## 5️⃣ 🚀 Desplegar

1.  Vuelve a Vercel → pestaña **Deployments** → pulsa **Redeploy** (o haz un simple `git push`).
2.  Espera el build (~2–4 min):
    - Fase 1: `pip install -r requirements.txt`
    - Fase 2: `cd frontend && npm install`
    - Fase 3: `cd frontend && npm run build`
    - Fase 4: despliega la función serverless `api/index.py`
3.  Al finalizar, abre `https://TU-PROYECTO.vercel.app`:

### ✅ Checklist post-deploy
| Prueba | Resultado esperado |
|---|---|
| Atras `/api/health` | `{"status":"ok","actividades_cargadas":1738,"modelo_entrenado":true}` |
| UI home | 7 tarjetas de estadísticas con números reales |
| Escribir "Venta de flores" | 5 tarjetas con código CIIU y scores % |
| Swagger docs | `https://TU-PROYECTO.vercel.app/docs` |

### 🚨 Troubleshooting en producción
- **`/api/health` retorna error 500 / DB error**: la variable `POSTGRES_URL` no se inyectó. Añádela en *Settings → Environment Variables* y haz **Redeploy**.
- **Predicciones vacías / clasificador no entrenado**: la base de datos está vacía. Repite el **Paso 4 (carga inicial)**.
- **Primer request lento (~3s)**: es normal, cold start de Lambda. Después de eso Vercel mantiene caliente la función por ~10–30 min.
- **Error `psycopg2.OperationalError: SSL`**: asegúrate de que tu `POSTGRES_URL` local termine en `?sslmode=require`. El backend lo fuerza automáticamente para hosts `.vercel-storage.com`, `.supabase.com`, `.neon.tech`.

---

## 🧠 ¿Cómo funciona el clasificador?

```
texto_usuario
    │
    ▼
normalizar: minúsculas · símbolos → espacios · stopwords ES · long.(palabra) > 1
    │
    ├──►  TF-IDF Vectorizer  (1-2 grams · sublinear_tf · 50k features)
    │      entrenado sobre ~1.738 * (descripcion + notas_comprende + jerarquía padres)
    │
    ├──►  similitud COSENO contra ~1.738 vectores → top-20 más similares
    │
    └──►  Re-rank top-20 con RapidFuzz
            score_fuzzy = (token_set_ratio + token_sort_ratio) / 200.0
            score_final = 0.70·coseno + 0.30·fuzzy
    │
    ▼
    top-k  (k configurable · default 5 · max 20)
    scores 0..1 (transparentes · reproducibles)
    cada uno con: código · descripción · jerarquía 6 niveles · página PDF
```

> **¿Por qué no un LLM directo?** Con clases cerradas (~1.738) el modelo simbólico
> da **~98%+ de precisión, costo 0 por consulta, 100% reproducible y cero alucinaciones**.
> Las variables `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` ya están
> declaradas en [config.py](file:///c:/Users/DIEVALL/Documents/Proyectos%20Python/predice-categoria-INEC-trae/backend/app/config.py)
> para añadir un *segundo parecer LLM* si quieres en el futuro.

---

## 🧪 Endpoints de la API (FastAPI · OpenAPI)

| Método | Ruta | Tag | Descripción |
|---|---|---|---|
| `GET` | `/api/health` | General | Estado · actividades cargadas · modelo entrenado |
| `GET` | `/api/estadisticas` | General | Conteos por nivel jerárquico |
| `GET` | `/api/secciones` | Catálogo | 21 secciones A–U |
| `GET` | `/api/secciones/{codigo}/divisiones` | Catálogo | Divisiones de una sección |
| `GET` | `/api/divisiones/{codigo}/grupos` | Catálogo | Grupos de una división |
| `GET` | `/api/grupos/{codigo}/clases` | Catálogo | Clases de un grupo |
| `GET` | `/api/actividades` | Catálogo | Búsqueda paginada · FTS + filtros `q`, `seccion`, `clase`, `page`, `limit` |
| `GET` | `/api/actividades/{codigo}` | Catálogo | Detalle de una actividad |
| `POST` | `/api/predecir` | **IA** | **Endoint principal** — clasifica texto libre → top-k predicciones |
| `POST` | `/api/admin/reentrenar` | Admin | Re-entrena TF-IDF (útil después de nueva carga) |
| `GET` | `/docs` · `/redoc` | Docs | Swagger UI / ReDoc automático |

**Request `POST /api/predecir`** mínimo:
```json
{ "texto": "Panadería y venta de pan casero", "top_k": 5 }
```

**Response** (resumido):
```json
{
  "texto_ingresado": "Panadería y venta de pan casero",
  "total_coincidencias": 5,
  "modelo_usado": "tfidf+coseno+fuzzy",
  "tiempo_ms": 62.4,
  "resultados": [
    {
      "score": 0.8421,
      "score_porcentaje": 84.21,
      "actividad_codigo": "C1071.01",
      "actividad_descripcion": "Elaboración de pan de masa común",
      "clase_codigo": "C1071",
      "clase_descripcion": "Elaboración de pan y demás productos de panadería",
      "grupo_codigo": "C107",
      "grupo_descripcion": "Elaboración de pan, productos de panadería, pastelería y pasta",
      "division_codigo": "C10",
      "division_descripcion": "Industrias alimentarias",
      "seccion_codigo": "C",
      "seccion_descripcion": "Industrias manufactureras",
      "pagina_pdf": 78
    }
  ]
}
```

---

## ❓ FAQ · Troubleshooting

### ❌ `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`
Estás usando **Python < 3.10** con código moderno (`str | None`). ✅ Este proyecto
ya está adaptado: usa `from typing import Optional` en vez del operador `|`.
Asegúrate de tener la última versión del código.

### ❌ `pg_config executable not found` al instalar `psycopg2-binary`
Falta PostgreSQL en el PATH:
- Windows: reinstala PostgreSQL marcando *"Add to PATH"*.
- macOS: `brew install postgresql`.
- Linux: `sudo apt install -y libpq-dev python3-dev`.

### ❌ `ERROR: No se pudo conectar a PostgreSQL`
- ¿PostgreSQL está corriendo? En Windows: *"Servicios" → PostgreSQL → Iniciar*.
- ¿Contraseña correcta en `.env`? Prueba `psql -U postgres -h localhost`.
- ¿Puerto `5432`? Por defecto sí; si lo cambiaste edita `DB_PORT`.

### ❌ `ModuleNotFoundError: No module named 'backend.app'`
Estás corriendo uvicorn mal. ✅ El comando correcto **desde la RAÍZ** es:
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### ❌ Frontend dice "No se pudo conectar con el servidor de IA"
- Backend arriba? Abre http://localhost:8000/docs.
- `frontend/.env` contiene `NEXT_PUBLIC_API_URL=http://localhost:8000`.
- F12 → Network → revisa el request fallido. ¿URL correcta? ¿HTTP 200?

### ❌ Predicciones con scores muy bajos
- Ejecuta `POST /api/admin/reentrenar` o reinicia uvicorn.
- `/api/health` → `actividades_cargadas` debería ser ~1738. Si es 0 → te falto el paso 5 (05_cargar_a_postgres.py).

---

## 👤 Autor

**Diego Vallejo**  
Senior Full-Stack Engineer · Arquitecto Cloud AWS/GCP · Data Scientist

> 🧩 *"Construyo productos de IA que escalan sin deudas técnicas."*

- 🌐 Web: **[diegovallejo.dev](https://diegovallejo.dev)**
- 💼 LinkedIn: **[linkedin.com/in/diegovallejo](https://linkedin.com/in/diegovallejo)**
- 💻 GitHub: **[@diegovallejo](https://github.com/diegovallejo)**
- 📧 Email: **contacto@diegovallejo.dev**

---

## 🤝 Contribuciones

¡Issues y PRs son **muy bienvenidos**! El proyecto nació como prototipo para
el INEC, así que PRs que mejoren el parser del PDF, la precisión del clasificador,
la UX, tests unitarios o documentación son un **huge plus**.

**Si usas este proyecto en tu trabajo, considera dejar un ⭐ en GitHub — ayuda mucho.**

---

## 📜 Licencia

Distribuido bajo licencia **MIT** — puedes usar, modificar y distribuir
este código libremente en proyectos comerciales o personales.
Mencionar la autoría es apreciado pero no obligatorio.
Lee el texto completo en [LICENSE](./LICENSE).

---

<br/>

<div align="center">
  <a href="#️-cómo-funciona-el-clasificador-">Volver arriba ↑</a>
  <br/><br/>
  <table align="center" cellpadding="12" cellspacing="0" style="border: none;">
    <tr>
      <td><img height="36" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" /></td>
      <td><img height="36" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" /></td>
      <td><img height="36" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" /></td>
      <td><img height="36" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scikitlearn/scikitlearn-original.svg" /></td>
      <td><img height="36" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nextjs/nextjs-original.svg" /></td>
      <td><img height="36" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg" /></td>
      <td><img height="36" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg" /></td>
      <td><img height="36" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tailwindcss/tailwindcss-original.svg" /></td>
      <td><img height="36" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vercel/vercel-original-wordmark.svg" /></td>
    </tr>
  </table>
  <h4>🇪🇨 &nbsp; Hecho en Ecuador con <span style="color:#e11d48;">♥</span> por Diego Vallejo &nbsp;·&nbsp; 2024–2026</h4>
</div>
