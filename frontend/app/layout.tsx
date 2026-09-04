import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CIIU Clasificador — INEC",
  description:
    "Clasificador automático de actividades económicas CIIU 4.0 del INEC con Inteligencia Artificial. Escribe una actividad y recibe la categoría oficial en tiempo real.",
  keywords: ["INEC", "CIIU", "Clasificación", "Actividades económicas", "Ecuador", "IA", "Diego Vallejo"],
  authors: [{ name: "Diego Vallejo" }],
  openGraph: {
    title: "CIIU Clasificador IA — INEC Ecuador",
    description: "Identifica la categoría CIIU oficial al escribir una actividad económica. Precisión casi 100%.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es-EC">
      <head>
        <link
          rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet" />
      </head>
      <body>{children}</body>
    </html>
  );
}
