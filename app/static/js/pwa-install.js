/**
 * Instalación PWA Patagonia Export — portal o admin.
 */
(function () {
  const root = document.getElementById('ps-pwa-install');
  if (!root) return;

  const profile = root.dataset.pwaProfile || 'portal';
  const swPath = profile === 'admin' ? '/admin/sw.js' : '/portal/sw.js';
  const scope = profile === 'admin' ? '/admin/' : '/portal/';
  const iconSrc = profile === 'admin'
    ? '/static/img/pwa/ship-admin-192.png'
    : '/static/img/pwa/ship-portal-192.png';

  const btn = document.getElementById('ps-pwa-install-btn');
  const iosHint = document.getElementById('ps-pwa-ios-hint');
  const desktopHint = document.getElementById('ps-pwa-desktop-hint');
  const installed = document.getElementById('ps-pwa-installed');
  let deferredPrompt = null;

  function isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches
      || window.navigator.standalone === true;
  }

  function isIos() {
    return /iphone|ipad|ipod/i.test(navigator.userAgent);
  }

  function showInstalled() {
    if (installed) installed.classList.remove('hidden');
    if (btn) btn.classList.add('hidden');
    if (iosHint) iosHint.classList.add('hidden');
    if (desktopHint) desktopHint.classList.add('hidden');
  }

  function registerSw() {
    if (!('serviceWorker' in navigator)) return;
    navigator.serviceWorker.register(swPath, { scope: scope }).catch(function () {});
  }

  registerSw();

  if (isStandalone()) {
    showInstalled();
    return;
  }

  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredPrompt = e;
    if (btn) btn.classList.remove('hidden');
    if (desktopHint) desktopHint.classList.add('hidden');
  });

  window.addEventListener('appinstalled', function () {
    deferredPrompt = null;
    showInstalled();
  });

  if (btn) {
    btn.addEventListener('click', async function () {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      deferredPrompt = null;
    });
  }

  if (isIos() && iosHint) {
    iosHint.classList.remove('hidden');
  } else if (desktopHint) {
    window.setTimeout(function () {
      if (!deferredPrompt && !isStandalone()) {
        desktopHint.classList.remove('hidden');
      }
    }, 2000);
  }

  var iconEl = document.getElementById('ps-pwa-install-icon');
  if (iconEl) iconEl.src = iconSrc;
})();
