import socket

HOST = '127.0.0.1'
PORT = 9999

# Structuri de memorie
clienti_conectati = set()
mesaje = {}  # Format: { id: {"addr": (ip, port), "text": "mesaj"} }
id_curent = 1


def run_server():
    global id_curent
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"Server UDP pornit pe {HOST}:{PORT}")

        while True:
            try:
                data, addr = s.recvfrom(1024)
                mesaj_receptionat = data.decode('utf-8').strip()

                # Impartim in comanda si argument (daca exista)
                parts = mesaj_receptionat.split(maxsplit=1)
                if not parts:
                    continue

                cmd = parts[0].upper()
                arg = parts[1] if len(parts) > 1 else ""
                raspuns = ""

                # --- LOGICA EXISTENTA ---
                if cmd == "CONNECT":
                    if addr in clienti_conectati:
                        raspuns = "ERROR: Deja conectat"
                    else:
                        clienti_conectati.add(addr)
                        raspuns = f"OK: Conectat. Clienti activi: {len(clienti_conectati)}"

                elif cmd == "DISCONNECT":
                    if addr in clienti_conectati:
                        clienti_conectati.remove(addr)
                        raspuns = "OK: Deconectat"
                    else:
                        raspuns = "ERROR: Nu esti conectat"

                # --- LOGICA NOUA IMPLEMENTATA ---
                elif cmd in ["PUBLISH", "DELETE", "LIST"]:
                    # 1. Verificare conexiune obligatorie
                    if addr not in clienti_conectati:
                        raspuns = "ERROR: Trebuie sa fii conectat pentru a folosi aceasta comanda"

                    elif cmd == "PUBLISH":
                        # 2. Verificare argument PUBLISH
                        if not arg:
                            raspuns = "ERROR: Mesajul nu poate fi gol"
                        else:
                            mesaje[id_curent] = {"addr": addr, "text": arg}
                            raspuns = f"OK: Mesaj publicat cu ID={id_curent}"
                            id_curent += 1

                    elif cmd == "DELETE":
                        # 3. Verificare tip argument si autorizare DELETE
                        try:
                            msg_id = int(arg)
                            if msg_id not in mesaje:
                                raspuns = "ERROR: ID negasit"
                            elif mesaje[msg_id]["addr"] != addr:
                                raspuns = "ERROR: Nu esti autorul acestui mesaj. Nu ai permisiunea de a-l sterge!"
                            else:
                                del mesaje[msg_id]
                                raspuns = f"OK: Mesajul {msg_id} a fost sters"
                        except ValueError:
                            raspuns = "ERROR: ID-ul trebuie sa fie un numar intreg"

                    elif cmd == "LIST":
                        # 4. Returnarea tuturor mesajelor
                        if not mesaje:
                            raspuns = "DATA: Nu exista mesaje publicate"
                        else:
                            linii = [f"ID={m_id} | {date['text']}" for m_id, date in mesaje.items()]
                            raspuns = "DATA:\n" + "\n".join(linii)

                else:
                    raspuns = "ERROR: Comanda necunoscuta"

                # Trimitem raspunsul la client
                s.sendto(raspuns.encode('utf-8'), addr)

            except Exception as e:
                print(f"Eroare server: {e}")


if __name__ == "__main__":
    run_server()