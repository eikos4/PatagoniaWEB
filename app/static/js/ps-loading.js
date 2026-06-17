/**
 * Splash de carga Patagonia Sur — cada pantalla y navegación interna.
 */
(function () {
  const splash = document.getElementById('ps-loading-splash');
  if (!splash) return;

  const MIN_MS = 400;
  const MAX_MS = 10000;
  const start = performance.now();
  let hiding = false;

  function show() {
    hiding = false;
    splash.classList.remove('ps-loading--hide');
    document.body.classList.add('ps-loading-active');
  }

  function hide() {
    if (hiding) return;
    hiding = true;
    const elapsed = performance.now() - start;
    const wait = Math.max(0, MIN_MS - elapsed);

    window.setTimeout(function () {
      splash.classList.add('ps-loading--hide');
      document.body.classList.remove('ps-loading-active');
    }, wait);
  }

  document.body.classList.add('ps-loading-active');

  if (document.readyState === 'complete') {
    hide();
  } else {
    window.addEventListener('load', hide, { once: true });
    window.setTimeout(hide, MAX_MS);
  }

  document.addEventListener('click', function (e) {
    const link = e.target.closest('a[href]');
    if (!link || link.target === '_blank' || link.hasAttribute('download')) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

    const href = link.getAttribute('href');
    if (!href || href.charAt(0) === '#' || href.indexOf('mailto:') === 0 || href.indexOf('tel:') === 0) {
      return;
    }

    try {
      const url = new URL(link.href, window.location.href);
      if (url.origin === window.location.origin && url.pathname !== window.location.pathname) {
        show();
      }
    } catch (err) { /* ignore */ }
  });

  document.addEventListener('submit', function (e) {
    const form = e.target;
    if (form && form.tagName === 'FORM' && !form.target) {
      show();
    }
  });
})();
