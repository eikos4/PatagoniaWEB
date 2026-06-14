# passenger_wsgi.py
import os
import sys

# 1) Añade el directorio del proyecto al path
BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 2) Limita hilos BLAS ANTES de cualquier import que toque numpy/scipy/sklearn
for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(k, "1")

# 3) Ajustes de entorno (opcional)
os.environ.setdefault("FLASK_ENV", "production")

# 4) Logging básico a archivo (opcional pero útil para ver errores en producción)
try:
    import logging
    from logging.handlers import RotatingFileHandler
    log_path = os.path.join(BASE_DIR, "wsgi_error.log")
    handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
except Exception:
    handler = None

# 5) Crea la app
from app import create_app
application = create_app()   # Passenger busca 'application'

# 6) Conecta el logger (si se creó)
if handler:
    application.logger.addHandler(handler)
    application.logger.setLevel(logging.INFO)