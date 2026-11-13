import importlib
import sys
from pathlib import Path

import pytest

SERVICE_DIR = str(Path(__file__).resolve().parent.parent)


def _preparar_entorno():
    """Deja visible únicamente el paquete ``app`` / ``run`` de este servicio."""
    for nombre in list(sys.modules):
        if nombre == 'app' or nombre.startswith('app.') or nombre == 'run':
            del sys.modules[nombre]

    if SERVICE_DIR in sys.path:
        sys.path.remove(SERVICE_DIR)
    sys.path.insert(0, SERVICE_DIR)


@pytest.fixture
def client():
    """Cliente del servidor simplificado definido en ``run.py``."""
    _preparar_entorno()
    modulo_run = importlib.import_module('run')
    modulo_run.app.config['TESTING'] = True
    with modulo_run.app.test_client() as cliente:
        yield cliente


@pytest.fixture
def api_client(tmp_path):
    """Cliente de la API persistente (paquete ``app``) con base temporal."""
    _preparar_entorno()
    paquete_app = importlib.import_module('app')
    base = tmp_path / 'drones-test.db'
    aplicacion = paquete_app.create_app({
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{base.as_posix()}'
    })
    aplicacion.config['TESTING'] = True
    with aplicacion.test_client() as cliente:
        yield cliente