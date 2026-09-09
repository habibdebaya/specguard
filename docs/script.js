(() => {
  'use strict';

  const browser = document.querySelector('.findings-browser');
  const track = document.querySelector('.findings-track');
  const panels = Array.from(track.querySelectorAll('.finding'));
  const index = document.querySelector('.finding-index');
  const links = Array.from(index.querySelectorAll('a'));
  const toolbar = document.querySelector('.finding-toolbar');
  const toggle = document.querySelector('.view-toggle');
  const previous = document.querySelector('.previous-finding');
  const next = document.querySelector('.next-finding');
  const announcement = document.querySelector('.finding-announcement');
  const narrow = window.matchMedia('(max-width: 740px)');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let current = 0;
  let stacked = narrow.matches;
  let chosenMode = false;
  let scrollFrame;
  let printing = false;

  function fitPanel() {
    if (!stacked && !printing) {
      track.style.height = `${panels[current].getBoundingClientRect().height + 16}px`;
    } else {
      track.style.removeProperty('height');
    }
  }

  function updateCurrent(value) {
    current = Math.max(0, Math.min(value, panels.length - 1));
    links.forEach((link, i) => {
      if (i === current) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
      panels[i].inert = !printing && !stacked && i !== current;
    });
    previous.disabled = current === 0;
    next.disabled = current === panels.length - 1;
    announcement.textContent = links[current].querySelector('strong').textContent;
    fitPanel();
  }

  function showPanel(value, { smooth = false, setHash = false, scrollPage = false } = {}) {
    updateCurrent(value);
    if (!stacked) {
      track.scrollTo({
        left: panels[current].offsetLeft,
        behavior: smooth && !reducedMotion.matches ? 'smooth' : 'instant',
      });
    }
    if (setHash) history.replaceState(null, '', `#${panels[current].id}`);
    if (scrollPage || stacked) panels[current].scrollIntoView({ block: 'start', behavior: 'instant' });
  }

  function setMode(value) {
    stacked = value;
    browser.classList.toggle('is-carousel', !stacked);
    browser.classList.toggle('is-stacked', stacked);
    toggle.textContent = stacked ? 'Browse one at a time' : 'Read all findings';
    toggle.setAttribute('aria-pressed', String(stacked));
    updateCurrent(current);
    if (!stacked) showPanel(current);
  }

  function panelForHash() {
    const match = window.location.hash.match(/^#finding-([1-5])$/);
    return match ? Number(match[1]) - 1 : null;
  }

  toolbar.hidden = false;
  setMode(stacked);
  const initial = panelForHash();
  if (initial !== null) requestAnimationFrame(() => showPanel(initial, { scrollPage: true }));

  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href^="#finding-"]');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const target = panels.findIndex(panel => `#${panel.id}` === link.getAttribute('href'));
    if (target === -1) return;
    event.preventDefault();
    const insidePanel = Boolean(link.closest('.finding'));
    showPanel(target, { smooth: !insidePanel, setHash: true, scrollPage: insidePanel || stacked });
    if (insidePanel) links[target].focus({ preventScroll: true });
  });

  index.addEventListener('keydown', (event) => {
    const focused = links.indexOf(event.target);
    if (focused === -1) return;
    let target;
    if (event.key === 'ArrowRight') target = Math.min(focused + 1, panels.length - 1);
    else if (event.key === 'ArrowLeft') target = Math.max(focused - 1, 0);
    else if (event.key === 'Home') target = 0;
    else if (event.key === 'End') target = panels.length - 1;
    else return;
    event.preventDefault();
    links[target].focus({ preventScroll: true });
    showPanel(target, { smooth: true, setHash: true });
  });

  previous.addEventListener('click', () => showPanel(current - 1, { smooth: true, setHash: true }));
  next.addEventListener('click', () => showPanel(current + 1, { smooth: true, setHash: true }));
  toggle.addEventListener('click', () => {
    chosenMode = true;
    setMode(!stacked);
  });

  track.addEventListener('scroll', () => {
    if (stacked || printing) return;
    cancelAnimationFrame(scrollFrame);
    scrollFrame = requestAnimationFrame(() => {
      if (stacked || printing) return;
      const closest = Math.round(track.scrollLeft / track.clientWidth);
      if (closest !== current) {
        updateCurrent(closest);
        history.replaceState(null, '', `#${panels[current].id}`);
      }
    });
  }, { passive: true });

  const resize = new ResizeObserver(fitPanel);
  panels.forEach(panel => resize.observe(panel));
  window.addEventListener('resize', () => {
    if (!stacked && !printing) showPanel(current);
  });
  narrow.addEventListener('change', () => {
    if (!chosenMode) setMode(narrow.matches);
  });
  window.addEventListener('hashchange', () => {
    const target = panelForHash();
    if (target !== null) showPanel(target, { scrollPage: true });
  });

  let closedEvidence = [];
  window.addEventListener('beforeprint', () => {
    printing = true;
    closedEvidence = Array.from(document.querySelectorAll('details:not([open])'));
    closedEvidence.forEach(details => { details.open = true; });
    panels.forEach(panel => { panel.inert = false; });
    fitPanel();
  });
  window.addEventListener('afterprint', () => {
    printing = false;
    closedEvidence.forEach(details => { details.open = false; });
    updateCurrent(current);
    if (!stacked) showPanel(current);
  });
  const print = document.querySelector('.print-report');
  print.hidden = false;
  print.addEventListener('click', () => window.print());
})();
