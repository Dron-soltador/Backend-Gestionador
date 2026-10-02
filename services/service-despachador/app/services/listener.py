import time
import threading
from app.services.pedidos_client import obtener_pedidos_pendientes, obtener_detalle_pedido, actualizar_estado_pedido

pedidos_procesados = set()

def procesar_pedido_automatico(pedido_id):
    """
    Lógica de procesamiento e intercambio de estado automático.
    """
    pedido, status = obtener_detalle_pedido(pedido_id)
    if status == 200 and pedido:
        peso = pedido.get("peso_kg", 0)
        urgente = pedido.get("es_urgente", False)
        print(f" -> [ASIGNADOR] Pedido #{pedido_id} procesado (Peso: {peso}kg, Urgente: {urgente}).")
        
        # Cambiar el estado en la base de datos de Pedidos del compañero
        res, st_code = actualizar_estado_pedido(pedido_id, "EN_CAMINO")
        if st_code in (200, 204):
            print(f" -> [ESTADO] Estado del Pedido #{pedido_id} actualizado exitosamente a 'EN_CAMINO' en el servidor remoto.")
        else:
            print(f" -> [ESTADO Error] No se pudo cambiar el estado del Pedido #{pedido_id}: {res}")
    else:
        print(f" -> [ASIGNADOR Error] No se pudieron obtener detalles del pedido #{pedido_id}.")

def bucle_escucha(intervalo_segundos=5):
    """
    Bucle continuo de consulta en segundo plano.
    """
    print(f"[LISTENER] Iniciado listener en segundo plano (consultando cada {intervalo_segundos}s)...")
    while True:
        try:
            pedidos, status = obtener_pedidos_pendientes()
            
            if status == 200:
                lista_pedidos = pedidos if isinstance(pedidos, list) else pedidos.get('data', [])
                
                for p in lista_pedidos:
                    p_id = p.get('id')
                    if p_id and p_id not in pedidos_procesados:
                        print(f"\n[LISTENER] ¡Nuevo pedido detectado! ID: {p_id}")
                        pedidos_procesados.add(p_id)
                        procesar_pedido_automatico(p_id)
        except Exception as e:
            print(f"[LISTENER Error]: Ocurrió un error en el hilo de escucha: {e}")
        
        time.sleep(intervalo_segundos)

def iniciar_listener():
    thread = threading.Thread(target=bucle_escucha, daemon=True)
    thread.start()