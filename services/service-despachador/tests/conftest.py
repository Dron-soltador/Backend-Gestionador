import pytest
import sys
from pathlib import Path

@pytest.fixture
def client():
    SERVICE_DIR = str(Path(__file__).resolve().parent.parent)
    
    for mod in list(sys.modules.keys()):
        if mod in ['app', 'run'] or mod.startswith(('app.', 'routes.')):
            del sys.modules[mod]

    if SERVICE_DIR in sys.path:
        sys.path.remove(SERVICE_DIR)
    sys.path.insert(0, SERVICE_DIR)

    try:
        from run import app
    except Exception:
        from app import app

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client