/**
 * Instalación PWA Patagonia Export — portal o admin.
 * Android: botón visible + barra inferior al detectar instalación.
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
  const androidBar = document.getElementById('ps-pwa-android-bar');
  const androidBarBtn = document.getElementById('ps-pwa-android-bar-btn');
  const androidWait = document.getElementById('ps-pwa-android-wait');
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

  function isAndroid() {
    return /android/i.test(navigator.userAgent);
  }

  function showInstalled() {
    if (installed) installed.classList.remove('hidden');
    if (btn) btn.classList.add('hidden');
    if (androidWait) androidWait.classList.add('hidden');
    if (iosHint) iosHint.classList.add('hidden');
    if (desktopHint) desktopHint.classList.add('hidden');
    hideAndroidBar();
  }

  function hideAndroidBar() {
    if (androidBar) androidBar.classList.remove('is-visible');
  }

  function showAndroidBar() {
    if (!isAndroid() || isStandalone() || !androidBar) return;
    androidBar.classList.add('is-visible');
    document.body.style.paddingBottom = 'calc(5.5rem + env(safe-area-inset-bottom, 0px))';
  }

  function setBtnReady(ready) {
    if (!btn) return;
    btn.disabled = !ready;
    btn.classList.toggle('opacity-60', !ready);
    btn.classList.toggle('cursor-wait', !ready);
  }

  async function triggerInstall() {
    if (!deferredPrompt) return false;
    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    deferredPrompt = null;
    hideAndroidBar();
    return true;
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

  if (isIos()) {
    if (btn) btn.classList.add('hidden');
    if (iosHint) iosHint.classList.remove('hidden');
  } else if (isAndroid()) {
    setBtnReady(false);
    if (androidWait) androidWait.classList.remove('hidden');
    showAndroidBar();
  } else {
    setBtnReady(false);
    if (btn) btn.classList.add('hidden');
  }

  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredPrompt = e;
    setBtnReady(true);
    if (androidWait) androidWait.classList.add('hidden');
    if (btn) btn.classList.remove('hidden');
    if (isAndroid()) {
      showAndroidBar();
    }
    if (desktopHint) desktopHint.classList.add('hidden');
  });

  window.addEventListener('appinstalled', function () {
    deferredPrompt = null;
    showInstalled();
    document.body.style.paddingBottom = '';
  });

  if (btn) {
    btn.addEventListener('click', function () {
      triggerInstall();
    });
  }

  if (androidBarBtn) {
    androidBarBtn.addEventListener('click', function () {
      triggerInstall();
    });
  }

  if (!isIos() && !isAndroid() && desktopHint) {
    window.setTimeout(function () {
      if (!deferredPrompt && !isStandalone()) {
        desktopHint.classList.remove('hidden');
        if (btn && deferredPrompt) btn.classList.remove('hidden');
      }
      if (deferredPrompt && btn) {
        btn.classList.remove('hidden');
        setBtnReady(true);
      }
    }, 1500);
  }

  window.setTimeout(function () {
    if (isAndroid() && !deferredPrompt && !isStandalone() && androidWait) {
      androidWait.innerHTML = '<i class="fas fa-circle-info mr-1"></i> Toca <strong>Instalar</strong> cuando el navegador lo habilite, o usa el menú ⋮ → <strong>Instalar aplicación</strong>.';
    }
  }, 8000);

  document.querySelectorAll('#ps-pwa-install-icon, #ps-pwa-android-bar-icon').forEach(function (el) {
    el.src = iconSrc;
  });
})();
