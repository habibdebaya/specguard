(() => {
  'use strict';

  // The page follows the system theme until the reader picks one with the toggle.
  const root = document.documentElement;
  const button = document.querySelector('.theme-toggle');
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const themeColor = document.querySelector('meta[name="theme-color"]');
  const colors = { light: '#f8f7f3', dark: '#141816' };

  const current = () => root.dataset.theme || (system.matches ? 'dark' : 'light');

  const sync = () => {
    const theme = current();
    button.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    if (themeColor) themeColor.setAttribute('content', colors[theme]);
  };

  button.addEventListener('click', () => {
    root.dataset.theme = current() === 'dark' ? 'light' : 'dark';
    sync();
  });
  system.addEventListener('change', sync);

  button.hidden = false;
  sync();
})();
