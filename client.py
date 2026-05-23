import socket

HOST = '127.0.0.1'
PORT = 65432

def porneste_client():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("=== Conectat cu succes la server ===")
            print("Scrie comenzile tale mai jos (Ex: ADD mere 10, LIST, QUIT):\n")

            while True:
                # Citim ce tastezi în terminal
                comanda = input("Client > ").strip()
                if not comanda:
                    continue

                # Trimitem comanda către server (cu \n la final)
                s.sendall((comanda + "\n").encode('utf-8'))

                # Primim răspunsul de la server
                raspuns = s.recv(1024).decode('utf-8').strip()
                print(f"Server: {raspuns}\n")

                # Dacă serverul trimite semnalul de închidere, oprim și clientul
                if "Goodbye!" in raspuns:
                    break

    except ConnectionRefusedError:
        print("Eroare: Serverul NU este pornit! Porneste mai intai server.py")
    except Exception as e:
        print(f"A aparut o eroare: {e}")

if __name__ == "__main__":
    porneste_client()