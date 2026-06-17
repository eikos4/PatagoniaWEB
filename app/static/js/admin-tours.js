/**
 * Tutoriales por módulo (Driver.js) y bienvenida guía de importación.
 */
(function () {
  const toursEl = document.getElementById('ps-module-tours');
  const activeNav = document.body.dataset.activeNav || '';
  const userId = document.body.dataset.userId || '0';
  const showWelcome = document.body.dataset.showWelcome === '1';
  let tours = {};

  try {
    tours = toursEl ? JSON.parse(toursEl.textContent || '{}') : {};
  } catch (e) {
    console.warn('[PS Tours] No se pudo leer la configuración de tours.', e);
  }

  function storageKey(suffix) {
    return 'ps_' + userId + '_' + suffix;
  }

  function tourSeenKey(module) {
    return storageKey('tour_seen_' + module);
  }

  function hasSeenTour(module) {
    try {
      return localStorage.getItem(tourSeenKey(module)) === '1';
    } catch (e) {
      return false;
    }
  }

  function markTourSeen(module) {
    try {
      localStorage.setItem(tourSeenKey(module), '1');
    } catch (e) { /* ignore */ }
  }

  function markWelcomeSeen() {
    try {
      localStorage.setItem(storageKey('import_welcome_seen'), '1');
    } catch (e) { /* ignore */ }
  }

  function welcomeSeen() {
    try {
      return localStorage.getItem(storageKey('import_welcome_seen')) === '1';
    } catch (e) {
      return false;
    }
  }

  function getDriverFactory() {
    if (window.driver && window.driver.js && typeof window.driver.js.driver === 'function') {
      return window.driver.js.driver;
    }
    if (typeof window.driver === 'function') {
      return window.driver;
    }
    return null;
  }

  function buildSteps(module) {
    const config = tours[module];
    if (!config || !config.steps) return [];

    return config.steps.filter(function (step) {
      if (!step.element) return false;
      try {
        return !!document.querySelector(step.element);
      } catch (e) {
        return false;
      }
    }).map(function (s) {
      return {
        element: s.element,
        popover: {
          title: s.title,
          description: s.description,
          side: s.side || 'bottom',
          align: s.align || 'start',
        },
      };
    });
  }

  function startTour(module, force) {
    const driverFactory = getDriverFactory();
    if (!driverFactory) {
      console.warn('[PS Tours] Driver.js no está cargado.');
      return false;
    }

    const steps = buildSteps(module);
    if (!steps.length) {
      console.warn('[PS Tours] Sin pasos visibles para el módulo:', module);
      return false;
    }

    const driver = driverFactory({
      showProgress: true,
      progressText: '{{current}} de {{total}}',
      nextBtnText: 'Siguiente',
      prevBtnText: 'Anterior',
      doneBtnText: 'Entendido',
      popoverClass: 'ps-driver-popover',
      onDestroyed: function () {
        if (!force) {
          markTourSeen(module);
        }
      },
      steps: steps,
    });

    driver.drive();
    return true;
  }

  function maybeAutoTour() {
    if (!activeNav || !tours[activeNav] || hasSeenTour(activeNav)) return;

    const welcomeModal = document.getElementById('psWelcomeGuideModal');
    const welcomeOpen = welcomeModal && welcomeModal.classList.contains('flex');

    if (showWelcome && !welcomeSeen() && welcomeOpen) {
      return;
    }

    startTour(activeNav, false);
  }

  window.PSAdminTours = {
    start: function (module, force) {
      return startTour(module || activeNav, !!force);
    },
    reset: function (module) {
      try {
        if (module) {
          localStorage.removeItem(tourSeenKey(module));
        } else {
          Object.keys(localStorage).forEach(function (key) {
            if (key.startsWith('ps_' + userId + '_tour_seen_')) {
              localStorage.removeItem(key);
            }
          });
        }
      } catch (e) { /* ignore */ }
    },
    markSeen: markTourSeen,
  };

  document.getElementById('btnTourModulo')?.addEventListener('click', function () {
    startTour(activeNav, true);
  });

  // Modal bienvenida guía importación (primer login)
  const welcomeModal = document.getElementById('psWelcomeGuideModal');

  function closeWelcome(goToGuide) {
    markWelcomeSeen();
    welcomeModal?.classList.remove('flex');
    if (goToGuide && welcomeModal?.dataset.guideUrl) {
      window.location.href = welcomeModal.dataset.guideUrl;
      return;
    }
    window.setTimeout(maybeAutoTour, 400);
  }

  if (welcomeModal && showWelcome && !welcomeSeen()) {
    welcomeModal.classList.add('flex');
  } else {
    window.setTimeout(maybeAutoTour, 700);
  }

  document.getElementById('psWelcomeGuideGo')?.addEventListener('click', function () {
    closeWelcome(true);
  });
  document.getElementById('psWelcomeGuideClose')?.addEventListener('click', function () {
    closeWelcome(false);
  });
  document.getElementById('psWelcomeGuideLater')?.addEventListener('click', function () {
    closeWelcome(false);
  });
  welcomeModal?.addEventListener('click', function (e) {
    if (e.target === welcomeModal) closeWelcome(false);
  });
})();
