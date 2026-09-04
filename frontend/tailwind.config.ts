import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        inec: {
          // Paleta inspirada en colores institucionales + moderno
          primary:   "#0B4F8C",   // azul corporativo oscuro
          secondary: "#1F8A70",   // verde esmeralda
          accent:    "#F59E0B",   // ámbar / dorado para CTA
          ink:       "#0F172A",   // slate-900
          muted:     "#64748B",   // slate-500
          bg:        "#F8FAFC",   // slate-50
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        card:   "0 4px 24px -6px rgba(15, 23, 42, 0.08)",
        glow:   "0 0 0 4px rgba(31, 138, 112, 0.15)",
      },
      backgroundImage: {
        "hero-gradient":
          "radial-gradient(1200px 600px at 0% -10%, rgba(11, 79, 140, 0.15), transparent 60%)," +
          "radial-gradient(900px 500px at 100% 0%, rgba(31, 138, 112, 0.12), transparent 60%)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-400px 0" },
          "100%": { backgroundPosition: "400px 0" },
        },
      },
      animation: {
        "fade-in": "fade-in 240ms ease-out both",
        shimmer:   "shimmer 1.4s linear infinite",
      },
    },
  },
  plugins: [],
};
export default config;
