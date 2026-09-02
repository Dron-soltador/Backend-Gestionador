import sys
import os

# Agregar la carpeta services/service-despachador al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app import create_app
from app.services.dispatcher import seleccionar_dron_optimo

class TestAlgoritmoDespachador(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_caso_borde_bateria_19_porciento_rechazado(self):
        """Caso Borde: Dron con 19% de batería debe ser rechazado."""
        drones = [
            {"id": 1, "modelo": "Dron 1", "capacidad_max_kg": 10.0, "bateria_porcentaje": 19, "estado": "DISPONIBLE"}
        ]
        dron, error = seleccionar_dron_optimo(5.0, drones)
        self.assertIsNone(dron)
        self.assertIsNotNone(error)
        self.assertIn("No hay drones disponibles", error)

    def test_caso_borde_sobrepeso_0_1_kg_rechazado(self):
        """Caso Borde: Peso de 5.1 kg en dron de 5.0 kg debe ser rechazado."""
        drones = [
            {"id": 1, "modelo": "Dron 1", "capacidad_max_kg": 5.0, "bateria_porcentaje": 100, "estado": "DISPONIBLE"}
        ]
        dron, error = seleccionar_dron_optimo(5.1, drones)
        self.assertIsNone(dron)
        self.assertIsNotNone(error)

    def test_bateria_20_porciento_es_aceptada(self):
        """Caso Límite: Batería exactamente al 20% debe ser aceptada."""
        drones = [
            {"id": 1, "modelo": "Dron 1", "capacidad_max_kg": 5.0, "bateria_porcentaje": 20, "estado": "DISPONIBLE"}
        ]
        dron, error = seleccionar_dron_optimo(4.0, drones)
        self.assertIsNotNone(dron)
        self.assertEqual(dron['id'], 1)

    def test_seleccion_menor_capacidad_sobrante(self):
        """Selecciona el dron con menor capacidad sobrante (optimización de recurso)."""
        drones = [
            {"id": 1, "modelo": "Grande", "capacidad_max_kg": 20.0, "bateria_porcentaje": 100, "estado": "DISPONIBLE"},
            {"id": 2, "modelo": "Ajustado", "capacidad_max_kg": 6.0, "bateria_porcentaje": 80, "estado": "DISPONIBLE"}
        ]
        dron, error = seleccionar_dron_optimo(5.0, drones)
        self.assertEqual(dron['id'], 2)

    def test_empate_capacidad_selecciona_mayor_bateria(self):
        """En caso de empate en capacidad sobrante, prioriza mayor batería."""
        drones = [
            {"id": 1, "modelo": "Dron A", "capacidad_max_kg": 10.0, "bateria_porcentaje": 70, "estado": "DISPONIBLE"},
            {"id": 2, "modelo": "Dron B", "capacidad_max_kg": 10.0, "bateria_porcentaje": 95, "estado": "DISPONIBLE"}
        ]
        dron, error = seleccionar_dron_optimo(5.0, drones)
        self.assertEqual(dron['id'], 2)

    def test_endpoint_post_despachar_http_400(self):
        """Prueba de integración HTTP: rechazo 400 cuando no hay drones aptos."""
        response = self.client.post('/despachar', json={
            "peso_kg": 10.0,
            "drones": [
                {"id": 1, "modelo": "Dron 1", "capacidad_max_kg": 5.0, "bateria_porcentaje": 100, "estado": "DISPONIBLE"}
            ]
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

if __name__ == '__main__':
    unittest.main()