/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'media', // Usa 'media' para detectar automáticamente el tema del sistema
  content: [
    './templates/**/*.html', // Asegúrate de incluir tus plantillas HTML
    './static/js/**/*.js',   // Incluye tus scripts JS si usas clases dinámicas
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#007bff', // Azul claro
          dark: '#0056b3',  // Azul oscuro
        },
        background: {
          light: '#ffffff', // Fondo claro
          dark: '#1a202c',  // Fondo oscuro
        },
        text: {
          light: '#1a202c', // Texto oscuro para fondo claro
          dark: '#ffffff',  // Texto claro para fondo oscuro
        },
      },
    },
  },
  plugins: [],
};

//  npx tailwindcss -i ./static/css/main.css -o ./static/css/output.css --watch
