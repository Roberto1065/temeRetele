import socket

HOST = '127.0.0.1'
PORT = 9999


def porneste_client():
    este_conectat = False

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(5.0)

        def trimite_comanda(mesaj_str):
            s.sendto(mesaj_str.encode('utf-8'), (HOST, PORT))
            try:
                data, _ = s.recvfrom(1024)
                return data.decode('utf-8')
            except socket.timeout:
                return "ERROR: Server timeout (nu a raspuns in 5 secunde)"

        print("=== Client UDP pornit ===")
        print("Comenzi: CONNECT, DISCONNECT, PUBLISH , DELETE , LIST, EXIT\n")

        while True:
            comanda_raw = input("Client > ").strip()
            if not comanda_raw:
                continue

            parts = comanda_raw.split(maxsplit=1)
            cmd = parts[0].upper()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "EXIT":
                print("Inchidere aplicatie...")
                break

            # --- VALIDARI LOCALE (CLIENT-SIDE) ---
            if cmd in ["PUBLISH", "DELETE", "LIST"]:
                if not este_conectat:
                    print("Eroare locala: Trebuie sa fii conectat la server. Scrie CONNECT mai intai.")
                    continue

            if cmd == "PUBLISH" and not arg:
                print("Eroare locala: Lipseste textul. Foloseste: PUBLISH mesajul tau")
                continue

            if cmd == "DELETE":
                try:
                    int(arg)
                except ValueError:
                    print("Eroare locala: ID-ul trebuie sa fie un numar intreg. Ex: DELETE 1")
                    continue

            # Trimiterea la server dupa ce a trecut de validari
            raspuns = trimite_comanda(comanda_raw)
            print(f"Server: {raspuns}")

            # Actualizarea starii locale in functie de raspuns
            if cmd == "CONNECT" and "OK" in raspuns:
                este_conectat = True
            elif cmd == "DISCONNECT" and "OK" in raspuns:
                este_conectat = False


if __name__ == "__main__":
    porneste_client()