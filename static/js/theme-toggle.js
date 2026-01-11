document.addEventListener('DOMContentLoaded', () => {
    const html = document.documentElement;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (prefersDark) {
        html.classList.add('dark');
    } else {
        html.classList.remove('dark');
    }
});
