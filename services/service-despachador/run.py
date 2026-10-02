from app import create_app
from app.services.listener import iniciar_listener

app = create_app()

if __name__ == '__main__':
    # Arranca el listener en segundo plano
    iniciar_listener()
    
    # Inicia el servidor HTTP del Despachador en el puerto 5002
    app.run(host='0.0.0.0', port=5002, debug=True)