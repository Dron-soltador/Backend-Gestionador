def test_seleccionar_dron_optimo_peso_invalido(dispatcher_module):
    dron, msg = dispatcher_module.seleccionar_dron_optimo(0, [])
    assert dron is None
    assert "mayor a 0" in msg

    dron, msg = dispatcher_module.seleccionar_dron_optimo(None, [])
    assert dron is None


def test_seleccionar_dron_optimo_sin_drones_aptos(dispatcher_module):
    drones = [
        {"id": 1, "estado": "MANTENIMIENTO", "bateria_porcentaje": 100, "capacidad_max_kg": 10},
        {"id": 2, "estado": "DISPONIBLE", "bateria_porcentaje": 15, "capacidad_max_kg": 10},
        {"id": 3, "estado": "DISPONIBLE", "bateria_porcentaje": 90, "capacidad_max_kg": 2}
    ]
    dron, msg = dispatcher_module.seleccionar_dron_optimo(5.0, drones)
    assert dron is None
    assert "No hay drones disponibles" in msg


def test_seleccionar_dron_optimo_seleccion_y_prioridad(dispatcher_module):
    drones = [
        {"id": 1, "estado": "DISPONIBLE", "bateria_porcentaje": 80, "capacidad_max_kg": 10},
        {"id": 2, "estado": "DISPONIBLE", "bateria_porcentaje": 50, "capacidad_max_kg": 5},
        {"id": 3, "estado": "DISPONIBLE", "bateria_porcentaje": 90, "capacidad_max_kg": 5}
    ]
    # Para un paquete de 3kg:
    # - Dron 1: sobra 7kg
    # - Dron 2: sobra 2kg, bat 50%
    # - Dron 3: sobra 2kg, bat 90%
    # Debe elegir Dron 3 (menor capacidad sobrante y mayor batería en empate)
    dron, msg = dispatcher_module.seleccionar_dron_optimo(3.0, drones)
    assert dron is not None
    assert dron["id"] == 3
    assert msg is None