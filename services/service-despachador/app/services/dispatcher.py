def seleccionar_dron_optimo(peso_kg, drones):
    """
    Evalúa y selecciona el dron óptimo para un envío según las reglas:
    1. Estado del dron debe ser 'DISPONIBLE'
    2. Batería del dron >= 20%
    3. Capacidad máxima del dron >= peso_kg

    Criterio de ordenamiento/prioridad:
    - Menor capacidad sobrante (capacidad_max_kg - peso_kg)
    - Mayor porcentaje de batería en caso de empate en capacidad
    """
    if peso_kg is None or peso_kg <= 0:
        return None, "El peso del paquete debe ser un número mayor a 0 kg."

    drones_aptos = []
    for drone in drones:
        # 1. Estado disponible
        if drone.get('estado') != 'DISPONIBLE':
            continue
        # 2. Regla Energética: Batería >= 20%
        if drone.get('bateria_porcentaje', 0) < 20:
            continue
        # 3. Regla Física: Capacidad >= Peso
        if drone.get('capacidad_max_kg', 0) < peso_kg:
            continue

        drones_aptos.append(drone)

    if not drones_aptos:
        return None, f"No hay drones disponibles que cumplan con la capacidad física (>= {peso_kg} kg) y el nivel mínimo de batería (>= 20%)."

    # Ordenar aptos:
    # 1. Capacidad sobrante ascendente (capacidad_max_kg - peso_kg)
    # 2. Batería descendente (-bateria_porcentaje)
    drones_aptos.sort(key=lambda d: (
        d['capacidad_max_kg'] - peso_kg,
        -d['bateria_porcentaje']
    ))

    return drones_aptos[0], None