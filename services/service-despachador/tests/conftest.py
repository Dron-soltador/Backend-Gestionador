import importlib
import sys
from pathlib import Path

import pytest

SERVICE_DIR = str(Path(__file__).resolve().parent.parent)


def _preparar_entorno():
    """Deja visible únicamente el paquete ``app`` de este microservicio."""
    for nombre in list(sys.modules):
        if nombre == 'app' or nombre.startswith('app.') or nombre == 'run':
            del sys.modules[nombre]

    if SERVICE_DIR in sys.path:
        sys.path.remove(SERVICE_DIR)
    sys.path.insert(0, SERVICE_DIR)


@pytest.fixture
def app_despachador():
    _preparar_entorno()
    paquete_app = importlib.import_module('app')
    return paquete_app.create_app()


@pytest.fixture
def client(app_despachador):
    app_despachador.config['TESTING'] = True
    with app_despachador.test_client() as cliente:
        yield cliente


@pytest.fixture
def listener_module(app_despachador):
    """Módulo listener cargado por la misma app que atiende el cliente."""
    return sys.modules['app.services.listener']


@pytest.fixture
def pedidos_client_module(app_despachador):
    """Módulo de acceso a la API de Pedidos cargado por la app."""
    return sys.modules['app.services.pedidos_client']


@pytest.fixture
def dispatcher_module(app_despachador):
    """Módulo con la lógica de selección de drones."""
    return importlib.import_module('app.services.dispatcher')