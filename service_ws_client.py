import websocket
import threading

def on_message(ws, message):
    print(" Message reçu :", message)
    # 👇 Optional: you can call an internal endpoint
    #  try:
    #     data = json.loads(message)
    # except json.JSONDecodeError as e:
    #     print(" Failed to decode JSON:", e)
    #     return
    #   try:
    #     response = requests.post("http://localhost:8001/update-device", json=data)
    #     print(" Forwarded to internal service:", response.status_code)
    # except requests.RequestException as e:
    #     print(" Failed to forward message:", e)

def on_error(ws, error):
    print(" Erreur :", error)

def on_close(ws, close_status_code, close_msg):
    print(" Connexion fermée")

def on_open(ws):
    print(" Connecté au serveur WebSocket")

def run():
    ws = websocket.WebSocketApp(
        "ws://localhost:9000/ws",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

thread = threading.Thread(target=run)
thread.start()
