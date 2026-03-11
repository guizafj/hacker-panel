/**
 * theme-toggle.js
 *
 * Gestiona el modo oscuro/claro para Hacker Panel.
 *
 * Lógica de prioridad:
 *   1. Si el usuario ha elegido manualmente un tema → usar localStorage
 *   2. Si no hay preferencia guardada → usar prefers-color-scheme del SO
 *
 * Aplica/quita la clase 'dark' en <html>, que es lo que necesitan tanto
 * Tailwind (darkMode: 'class') como los selectores .dark de markdown.css.
 *
 * Se ejecuta lo antes posible para evitar el "flash" de tema incorrecto.
 */

(function () {
    const html = document.documentElement;
    const STORAGE_KEY = 'hp-theme';

    function getPreferredTheme() {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved === 'dark' || saved === 'light') return saved;
        // Fallback: preferencia del sistema operativo
        return window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light';
    }

    function applyTheme(theme) {
        if (theme === 'dark') {
            html.classList.add('dark');
        } else {
            html.classList.remove('dark');
        }
    }

    // Aplicar tema inmediatamente (antes del DOMContentLoaded para evitar flash)
    applyTheme(getPreferredTheme());

    // Escuchar cambios en la preferencia del SO (solo si no hay preferencia manual)
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem(STORAGE_KEY)) {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    });

    /**
     * toggleTheme() — función global para el botón de cambio de tema.
     *
     * Uso en cualquier template:
     *   <button onclick="toggleTheme()">Toggle</button>
     *
     * O desde JS:
     *   window.toggleTheme();
     */
    window.toggleTheme = function () {
        const current = html.classList.contains('dark') ? 'dark' : 'light';
        const next = current === 'dark' ? 'light' : 'dark';
        localStorage.setItem(STORAGE_KEY, next);
        applyTheme(next);
    };

    /**
     * isDarkMode() — consulta el tema activo.
     * Útil para adaptar gráficas, calendarios, etc.
     */
    window.isDarkMode = function () {
        return html.classList.contains('dark');
    };

})();