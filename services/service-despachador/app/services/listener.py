import logging
import time
import threading
from app.services.pedidos_client import obtener_pedidos_pendientes, obtener_detalle_pedido, actualizar_estado_pedido

logger = logging.getLogger(__name__)

pedidos_procesados = set()
pedidos_memoria = {}

def procesar_pedido_automatico(pedido_id):
    pedido, status = obtener_detalle_pedido(pedido_id)
    if status == 200 and pedido:
        peso = pedido.get("peso_kg", 0)
        urgente = pedido.get("es_urgente", False)
        logger.info(" -> [ASIGNADOR] Pedido #%s procesado (Peso: %skg, Urgente: %s).", pedido_id, peso, urgente)
        
        pedidos_memoria[pedido_id] = pedido
        
        res, st_code = actualizar_estado_pedido(pedido_id, "EN_CAMINO")
        if st_code in (200, 204):
            pedidos_memoria[pedido_id]["estado"] = "EN_CAMINO"
            logger.info(" -> [ESTADO] Pedido #%s actualizado a 'EN_CAMINO'.", pedido_id)
        else:
            logger.error(" -> [ESTADO Error] No se pudo cambiar estado: %s", res)
    else:
        logger.error(" -> [ASIGNADOR Error] No se obtuvieron detalles del pedido #%s.", pedido_id)

def bucle_escucha(intervalo_segundos=5):
    logger.info("[LISTENER] Escuchando en segundo plano (cada %ss)...", intervalo_segundos)
    while True:
        try:
            pedidos, status = obtener_pedidos_pendientes()
            if status == 200:
                lista_pedidos = pedidos if isinstance(pedidos, list) else pedidos.get('data', [])
                for p in lista_pedidos:
                    p_id = p.get('id')
                    if p_id and p_id not in pedidos_procesados:
                        logger.info("\n[LISTENER] ¡Nuevo pedido detectado! ID: %s", p_id)
                        pedidos_procesados.add(p_id)
                        procesar_pedido_automatico(p_id)
        except Exception as e:
            logger.error("[LISTENER Error]: %s", e)
        time.sleep(intervalo_segundos)

def iniciar_listener():
    thread = threading.Thread(target=bucle_escucha, daemon=True)
    thread.start()