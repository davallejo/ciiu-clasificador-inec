"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import type { PredictResponse, PrediccionItem, Estadisticas } from "./lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

const EJEMPLOS = [
  "Panadería y venta de pan casero",
  "Restaurante de comida rápida con entrega a domicilio",
  "Cultivo de rosas y flores para exportación",
  "Reparación de celulares y accesorios",
  "Desarrollo de software y aplicaciones móviles",
  "Venta de ropa por catálogo por internet",
  "Transporte de pasajeros en taxi",
];

/* -------------------- Componentes pequeños -------------------- */

function LogoInec() {
  // Logo estilo institucional (SVG simple, no usa imágenes externas)
  return (
    <svg width="40" height="40" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="2" width="44" height="44" rx="10" fill="url(#g1)" />
      <path d="M13 15h22M13 24h16M13 33h12" stroke="#fff" strokeWidth="3" strokeLinecap="round"/>
      <circle cx="35" cy="33" r="5" fill="#F59E0B" />
      <defs>
        <linearGradient id="g1" x1="0" y1="0" x2="48" y2="48">
          <stop stopColor="#0B4F8C"/>
          <stop offset="1" stopColor="#1F8A70"/>
        </linearGradient>
      </defs>
    </svg>
  );
}

function SeccionBadge({ letra, nombre }: { letra: string; nombre: string }) {
  return (
    <span className="section-chip inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700 ring-1 ring-slate-200">
      <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-inec-primary text-[11px] font-bold text-white">
        {letra}
      </span>
      <span className="truncate max-w-[260px]">{nombre}</span>
    </span>
  );
}

function ScoreBar({ value }: { value: number }) {
  const pct = Math.max(0, Math.min(100, value));
  const color =
    pct >= 80 ? "from-emerald-500 to-teal-600"
    : pct >= 55 ? "from-sky-500 to-indigo-600"
    : pct >= 35 ? "from-amber-500 to-orange-600"
    : "from-rose-400 to-rose-600";
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
      <div
        className={`h-full rounded-full bg-gradient-to-r ${color} transition-all duration-500`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

function ResultCard({ item, rank }: { item: PrediccionItem; rank: number }) {
  return (
    <article
      className="group relative animate-fade-in rounded-2xl border border-slate-200 bg-white p-5 shadow-card transition hover:-translate-y-0.5 hover:border-inec-primary/30 hover:shadow-[0_12px_32px_-12px_rgba(11,79,140,0.25)]"
    >
      {/* Rank badge */}
      <div className="absolute -left-3 -top-3 flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-inec-primary to-inec-secondary text-sm font-extrabold text-white shadow-glow">
        {rank}
      </div>

      {/* Cabecera: código + score */}
      <header className="mb-3 flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <code className="rounded-lg bg-slate-900 px-2.5 py-1 font-mono text-sm font-bold tracking-wider text-emerald-300">
              {item.actividad_codigo}
            </code>
            <span className="rounded-md bg-amber-50 px-2 py-0.5 text-[11px] font-semibold text-amber-700 ring-1 ring-amber-200">
              NIVEL DETALLADO · 6 dígitos
            </span>
          </div>
          <h3 className="mt-2 text-lg font-bold leading-snug text-slate-900">
            {item.actividad_descripcion}
          </h3>
        </div>
        <div className="w-28 shrink-0 text-right">
          <div className="text-2xl font-extrabold text-inec-primary tabular-nums">
            {item.score_porcentaje.toFixed(1)}
            <span className="text-base font-semibold text-slate-400">%</span>
          </div>
          <div className="mt-2">
            <ScoreBar value={item.score_porcentaje} />
          </div>
        </div>
      </header>

      {/* Miga de pan: Jerarquía CIIU */}
      <div className="mt-3 flex flex-wrap items-center gap-2 text-[12px]">
        <SeccionBadge letra={item.seccion_codigo} nombre={item.seccion_descripcion} />

        {[
          [item.division_codigo, item.division_descripcion],
          [item.grupo_codigo, item.grupo_descripcion],
          [item.clase_codigo, item.clase_descripcion],
          ...(item.subclase_codigo ? [[item.subclase_codigo, item.subclase_descripcion]] as any : []),
        ].map(([c, d], i) => (
          <span key={i as number} className="inline-flex items-center gap-1.5 rounded-full bg-white px-2.5 py-1 text-slate-600 ring-1 ring-slate-200">
            <span className="font-mono font-bold text-slate-900">{c}</span>
            <span className="text-slate-500 max-w-[140px] truncate">{d}</span>
          </span>
        ))}
      </div>

      {/* Footer: página PDF */}
      {item.pagina_pdf && (
        <footer className="mt-4 flex items-center gap-2 border-t border-dashed border-slate-200 pt-3 text-xs text-slate-500">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          Página {item.pagina_pdf} del catálogo oficial CIIU 4.0 INEC
        </footer>
      )}
    </article>
  );
}

function StatCard({ label, value, accent }: { label: string; value: string | number; accent?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-card">
      <div className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</div>
      <div className={`mt-1 text-2xl font-extrabold tabular-nums ${accent || "text-inec-primary"}`}>{value}</div>
    </div>
  );
}

/* -------------------- Página principal -------------------- */

export default function HomePage() {
  const [texto, setTexto] = useState("");
  const [loading, setLoading] = useState(false);
  const [respuesta, setRespuesta] = useState<PredictResponse | null>(null);
  const [estadisticas, setEstadisticas] = useState<Estadisticas | null>(null);
  const [error, setError] = useState<string | null>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  /* Cargar estadísticas iniciales */
  useEffect(() => {
    let cancelado = false;
    fetch(`${API_BASE}/api/estadisticas`)
      .then((r) => {
        if (!r.ok) {
          console.warn("[estadisticas] HTTP no OK:", r.status, r.statusText);
          return null;
        }
        return r.json();
      })
      .then((d) => {
        if (!cancelado && d) setEstadisticas(d);
      })
      .catch((e) => {
        console.warn("[estadisticas] No se pudo conectar al backend:", e?.message || e);
      });
    return () => { cancelado = true; };
  }, []);

  /* Llamar a la IA con debounce */
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!texto || texto.trim().length < 2) {
      setRespuesta(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    debounceRef.current = setTimeout(() => {
      const controller = new AbortController();
      const url = `${API_BASE}/api/predecir`;
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto, top_k: 5 }),
        signal: controller.signal,
      })
        .then((r) => {
          if (!r.ok) {
            console.warn("[predecir] HTTP no OK:", r.status, r.statusText, "URL:", url);
            return r.json().catch(() => ({ advertencia: `Error del servidor: ${r.status} ${r.statusText}` }));
          }
          return r.json();
        })
        .then((data: PredictResponse) => {
          setRespuesta(data);
          setError(null);
        })
        .catch((e) => {
          if (e.name !== "AbortError") {
            console.error("[predecir] Fetch falló URL:", url, "Error:", e?.message || e);
            const detalle = API_BASE
              ? `Verifica que el backend esté corriendo en ${API_BASE} (puerto 8000).`
              : "Verifica que el backend esté corriendo y que BACKEND_URL esté configurado.";
            setError(`No se pudo conectar con el servidor de IA. ${detalle}`);
          }
        })
        .finally(() => setLoading(false));
    }, 500);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [texto]);

  const topResult = respuesta?.resultados[0] ?? null;

  return (
    <div className="min-h-screen bg-inec-bg text-inec-ink">
      {/* ====== NAV ====== */}
      <nav className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/70 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <a href="#" className="flex items-center gap-3">
            <LogoInec />
            <div className="leading-tight">
              <div className="text-sm font-extrabold text-slate-900">CIIU Clasificador</div>
              <div className="text-[11px] font-medium text-slate-500">
                INEC · Catálogo Oficial 4.0
              </div>
            </div>
          </a>
          <div className="hidden items-center gap-2 sm:flex">
            <span className="rounded-full bg-emerald-50 px-3 py-1 text-[11px] font-semibold text-emerald-700 ring-1 ring-emerald-200">
              <span className="mr-1 inline-block h-2 w-2 animate-pulse rounded-full bg-emerald-500 align-middle" />
              IA Activa
            </span>
            <a
              href="https://wa.me/593983320872"
              target="_blank"
              rel="noreferrer"
              className="rounded-lg px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
            >
              Diego Vallejo ↗
            </a>
          </div>
        </div>
      </nav>

      {/* ====== HERO / BUSCADOR ====== */}
      <section className="relative bg-hero-gradient">
        <div className="mx-auto max-w-7xl px-4 pb-12 pt-10 sm:px-6 sm:pt-16 lg:px-8 lg:pt-20">
          <div className="mx-auto max-w-4xl text-center">
            <span className="inline-flex items-center gap-2 rounded-full border border-inec-primary/20 bg-white/70 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-inec-primary shadow-sm backdrop-blur">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 2l2.4 7.4H22l-6.2 4.5L18.2 22 12 17.5 5.8 22l2.4-8.1L2 9.4h7.6z" />
              </svg>
              PROTOTIPO INICIAL Y OFICIAL PARA INEC
            </span>
            <h1 className="mt-4 text-balance text-4xl font-black leading-tight tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
              Describe una actividad económica y la IA la{" "}
              <span className="bg-gradient-to-r from-inec-primary via-sky-700 to-inec-secondary bg-clip-text text-transparent">
                clasifica al instante
              </span>
            </h1>
            <p className="mx-auto mt-5 max-w-2xl text-base leading-relaxed text-slate-600 sm:text-lg">
              Basado en el catálogo CIIU 4.0 del{" "}
              <span className="font-semibold text-slate-900">Instituto Nacional de Estadística y Censos (INEC)</span>.
              ~1.724 actividades detalladas, sin alucinaciones, con trazabilidad página por página al documento original.
            </p>

            {/* ====== INPUT ====== */}
            <div className="relative mx-auto mt-8 max-w-3xl">
              <div className="ribbon-shadow rounded-3xl border border-slate-200 bg-white p-2 sm:p-3">
                <div className="relative">
                  <textarea
                    value={texto}
                    onChange={(e) => setTexto(e.target.value)}
                    placeholder="Escribe aquí la actividad, ejemplo: 'Venta de café y empanadas en local pequeño'..."
                    rows={3}
                    className="ciiu-input w-full resize-none rounded-2xl border-0 bg-slate-50 px-5 py-4 text-base font-medium text-slate-900 outline-none ring-0 placeholder:text-slate-400 focus:bg-white focus:ring-2 focus:ring-inec-primary/40 sm:text-lg"
                  />
                  <div className="pointer-events-none absolute right-4 top-4 flex items-center gap-1 text-[11px] font-medium text-slate-400">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="11" cy="11" r="7" />
                      <line x1="21" y1="21" x2="16.65" y2="16.65" />
                    </svg>
                    BÚSQUEDA EN TIEMPO REAL
                  </div>
                </div>

                {/* Chips de ejemplo */}
                <div className="mt-2 flex flex-wrap items-center gap-2 px-2 pb-1 pt-1">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    Probar:
                  </span>
                  {EJEMPLOS.slice(0, 5).map((e) => (
                    <button
                      key={e}
                      onClick={() => setTexto(e)}
                      className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium text-slate-600 transition hover:border-inec-primary/40 hover:bg-inec-primary/5 hover:text-inec-primary"
                    >
                      {e}
                    </button>
                  ))}
                </div>
              </div>

              {/* Estado / advertencia */}
              <div className="mt-3 min-h-[20px] text-sm">
                {error && (
                  <span className="inline-flex items-center gap-1.5 rounded-md bg-rose-50 px-2.5 py-1 text-rose-700 ring-1 ring-rose-200">
                    ⚠ {error}
                  </span>
                )}
                {!error && loading && (
                  <span className="inline-flex items-center gap-2 text-slate-500">
                    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-inec-primary align-middle" />
                    Analizando texto con el modelo...
                  </span>
                )}
                {!error && !loading && respuesta?.advertencia && (
                  <span className="inline-flex items-center gap-1.5 rounded-md bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700 ring-1 ring-amber-200">
                    ℹ️ {respuesta.advertencia}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Estadísticas */}
          <div className="mx-auto mt-14 grid max-w-5xl grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
            {[
              ["Secciones",   estadisticas?.secciones   ?? "—", "text-indigo-700"],
              ["Divisiones",  estadisticas?.divisiones  ?? "—", "text-sky-700"],
              ["Grupos",      estadisticas?.grupos      ?? "—", "text-teal-700"],
              ["Clases",      estadisticas?.clases      ?? "—", "text-emerald-700"],
              ["Subclases",   estadisticas?.subclases   ?? "—", "text-lime-700"],
              ["Actividades", estadisticas?.actividades ?? "—", "text-inec-primary"],
              ["Exclusiones", estadisticas?.exclusiones ?? "—", "text-slate-700"],
            ].map(([l, v, c]) => (
              <StatCard key={l as string} label={l as string} value={v as string | number} accent={c as string} />
            ))}
          </div>
        </div>
      </section>

      {/* ====== RESULTADOS ====== */}
      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-5xl">
          {/* Cabecera resultados */}
          {respuesta?.resultados && respuesta.resultados.length > 0 && topResult && (
            <div className="animate-fade-in mb-6 flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-end">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-inec-secondary">
                  Coincidencia principal · Score {topResult.score_porcentaje.toFixed(1)}%
                </div>
                <h2 className="mt-1 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
                  {topResult.actividad_descripcion}
                  <span className="ml-3 align-middle font-mono text-base font-bold text-inec-primary">
                    {topResult.actividad_codigo}
                  </span>
                </h2>
              </div>
              <div className="text-xs text-slate-500">
                {respuesta.resultados.length} candidatos ·{" "}
                <span className="font-semibold text-slate-700">{respuesta.tiempo_ms.toFixed(0)} ms</span> ·{" "}
                modelo: <span className="font-mono font-semibold">{respuesta.modelo_usado}</span>
              </div>
            </div>
          )}

          {!respuesta && !loading && (
            <div className="animate-fade-in mx-auto mt-10 max-w-2xl rounded-3xl border border-dashed border-slate-300 bg-white/60 p-10 text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-inec-primary to-inec-secondary text-white shadow-glow">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                </svg>
              </div>
              <h3 className="text-xl font-bold text-slate-900">Comienza a escribir para ver resultados</h3>
              <p className="mt-2 text-sm text-slate-500">
                El modelo analiza tu texto mientras escribes, con un retardo de 500ms,
                y muestra las 5 actividades más probables del catálogo CIIU 4.0.
              </p>
            </div>
          )}

          {loading && !respuesta && (
            <div className="space-y-4">
              {[0, 1, 2].map((i) => (
                <div key={i} className="h-44 rounded-2xl skeleton" />
              ))}
            </div>
          )}

          {respuesta?.resultados && respuesta.resultados.length > 0 && (
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              {respuesta.resultados.map((r, idx) => (
                <ResultCard key={`${r.actividad_codigo}-${idx}`} item={r} rank={idx + 1} />
              ))}
            </div>
          )}

          {respuesta && respuesta.resultados.length === 0 && (
            <div className="mx-auto max-w-2xl rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-800">
              <div className="font-semibold">Sin coincidencias</div>
              <p className="mt-1 text-sm">
                Intenta con un texto más descriptivo o corrige posibles errores de digitación.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* ====== FOOTER ====== */}
      <footer className="border-t border-slate-200 bg-white/60">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 py-8 sm:flex-row sm:px-6 lg:px-8">
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <LogoInec />
            <div>
              <div className="font-semibold text-slate-900">CIIU Clasificador IA</div>
              <div className="text-xs">Catálogo oficial INEC · CIIU Rev. 4 · Ecuador</div>
            </div>
          </div>
          <div className="text-center text-xs text-slate-500 sm:text-right">
            <div className="font-semibold text-slate-700">Desarrollado por Diego Vallejo</div>
            <div>Arquitectura: Next.js 14 · FastAPI · PostgreSQL · scikit-learn + RapidFuzz</div>
            <div className="mt-1">© {new Date().getFullYear()} — Todos los derechos reservados</div>
          </div>
        </div>
      </footer>
    </div>
  );
}
