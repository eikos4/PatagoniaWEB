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
  const androidBar = document.getElementById('ps-pwa-android-bar');
  const androidBarBtn = document.getElementById('ps-pwa-android-bar-btn');
  const androidWait = document.getElementById('ps-pwa-android-wait');
  const iosHint = document.getElementById('ps-pwa-ios-hint');
  const desktopHint = document.getElementById('ps-pwa-desktop-hint');
  const fallback = document.getElementById('ps-pwa-fallback');
  const httpsWarn = document.getElementById('ps-pwa-https-warn');
  const installed = document.getElementById('ps-pwa-installed');
  let deferredPrompt = window.__psPwaPrompt || null;

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
    if (fallback) fallback.classList.add('hidden');
    hideAndroidBar();
  }

  function hideAndroidBar() {
    if (androidBar) androidBar.classList.remove('is-visible');
    document.body.style.paddingBottom = '';
  }

  function showAndroidBar() {
    if (!isAndroid() || isStandalone() || !androidBar) return;
    androidBar.classList.add('is-visible');
    document.body.style.paddingBottom = 'calc(5.5rem + env(safe-area-inset-bottom, 0px))';
  }

  function setInstallReady(ready) {
    if (btn) {
      btn.disabled = !ready;
      btn.classList.toggle('opacity-60', !ready);
      btn.classList.toggle('cursor-not-allowed', !ready);
    }
    if (androidBarBtn) {
      androidBarBtn.disabled = !ready;
      androidBarBtn.style.opacity = ready ? '1' : '0.55';
    }
  }

  function showFallback() {
    if (!fallback) return;
    fallback.classList.remove('hidden');
    if (!window.isSecureContext && httpsWarn) {
      httpsWarn.classList.remove('hidden');
    }
    if (androidWait) androidWait.classList.add('hidden');
  }

  function onInstallable(e) {
    if (e && e.preventDefault) {
      e.preventDefault();
      deferredPrompt = e;
    } else if (window.__psPwaPrompt) {
      deferredPrompt = window.__psPwaPrompt;
    }
    if (!deferredPrompt) return;

    setInstallReady(true);
    if (androidWait) androidWait.classList.add('hidden');
    if (fallback) fallback.classList.add('hidden');
    if (btn) btn.classList.remove('hidden');
    if (isAndroid()) showAndroidBar();
    if (desktopHint) desktopHint.classList.add('hidden');
  }

  function triggerInstall() {
    if (!deferredPrompt) {
      showFallback();
      return;
    }

    try {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then(function () {
        deferredPrompt = null;
        window.__psPwaPrompt = null;
        hideAndroidBar();
      });
    } catch (err) {
      showFallback();
    }
  }

  function registerSw() {
    if (!('serviceWorker' in navigator)) return Promise.resolve();
    return navigator.serviceWorker.register(swPath, { scope: scope }).catch(function () {});
  }

  registerSw().then(function () {
    if (deferredPrompt) onInstallable();
  });

  if (isStandalone()) {
    showInstalled();
    return;
  }

  setInstallReady(false);

  if (isIos()) {
    if (btn) btn.classList.add('hidden');
    if (iosHint) iosHint.classList.remove('hidden');
  } else if (isAndroid()) {
    if (androidWait) androidWait.classList.remove('hidden');
    showAndroidBar();
    if (!window.isSecureContext) {
      window.setTimeout(showFallback, 500);
    }
  } else {
    if (btn) btn.classList.add('hidden');
  }

  window.addEventListener('beforeinstallprompt', onInstallable);
  window.addEventListener('ps-pwa-installable', function () {
    onInstallable();
  });

  window.addEventListener('appinstalled', function () {
    deferredPrompt = null;
    window.__psPwaPrompt = null;
    showInstalled();
  });

  if (btn) {
    btn.addEventListener('click', triggerInstall);
  }

  if (androidBarBtn) {
    androidBarBtn.addEventListener('click', triggerInstall);
  }

  if (!isIos() && !isAndroid() && desktopHint) {
    window.setTimeout(function () {
      if (!deferredPrompt && !isStandalone()) {
        desktopHint.classList.remove('hidden');
      }
      if (deferredPrompt) {
        if (btn) btn.classList.remove('hidden');
        setInstallReady(true);
      }
    }, 1500);
  }

  window.setTimeout(function () {
    if (!deferredPrompt && !isStandalone() && isAndroid()) {
      showFallback();
    }
  }, 6000);

  document.querySelectorAll('#ps-pwa-install-icon, #ps-pwa-android-bar-icon').forEach(function (el) {
    el.src = iconSrc;
  });
})();
