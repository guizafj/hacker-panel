/** @type {import('tailwindcss').Config} */
module.exports = {
  // FIX: cambiado de 'media' a 'class'.
  // Con 'media' Tailwind aplicaba dark: via @media (prefers-color-scheme: dark),
  // pero markdown.css usa selectores .dark .markdown-body que requieren la clase
  // en <html>. Con 'class' ambos sistemas son consistentes: theme-toggle.js
  // añade/quita la clase 'dark' en <html> y todo funciona coordinado.
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#007bff',
          dark: '#0056b3',
        },
        background: {
          light: '#ffffff',
          dark: '#1a202c',
        },
        text: {
          light: '#1a202c',
          dark: '#ffffff',
        },
      },
    },
  },
  plugins: [],
};

// Recompilar tras este cambio:
// npx tailwindcss -i ./static/css/main.css -o ./static/css/output.css --watch