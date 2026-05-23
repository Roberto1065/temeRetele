import socket

HOST = '127.0.0.1'
PORT = 65432

# Dicționarul menținut în memorie
dic = {}


def handle_client(conn, addr):
    print(f"Client conectat: {addr}")
    while True:
        try:
            # Citim datele de la client
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break

            parts = data.split()
            if not parts:
                continue

            cmd = parts[0].upper()
            response = ""

            # ADD -> param cheie valoare
            if cmd == "ADD" and len(parts) >= 3:
                key = parts[1]
                value = " ".join(parts[2:])
                dic[key] = value
                response = "OK - record add"

            # GET -> param cheie
            elif cmd == "GET" and len(parts) == 2:
                key = parts[1]
                if key in dic:
                    response = f"DATA {dic[key]}"
                else:
                    response = "ERROR invalid key"

            # REMOVE -> param cheie
            elif cmd == "REMOVE" and len(parts) == 2:
                key = parts[1]
                if key in dic:
                    del dic[key]
                    response = "OK value deleted"
                else:
                    response = "ERROR invalid key"

            # LIST -> returnează tot formatat
            elif cmd == "LIST":
                if dic:
                    pairs = [f"{k}={v}" for k, v in dic.items()]
                    response = f"DATA|{','.join(pairs)}"
                else:
                    response = "DATA|empty"

            # COUNT -> returnează numărul de elemente
            elif cmd == "COUNT":
                response = f"DATA {len(dic)}"

            # CLEAR -> șterge tot
            elif cmd == "CLEAR":
                dic.clear()
                response = "all data deleted"

            # UPDATE -> param cheie valoare_noua
            elif cmd == "UPDATE" and len(parts) >= 3:
                key = parts[1]
                if key in dic:
                    value = " ".join(parts[2:])
                    dic[key] = value
                    response = "Data updated"
                else:
                    response = "ERROR invalid key"

            # POP -> param cheie (returnează și șterge)
            elif cmd == "POP" and len(parts) == 2:
                key = parts[1]
                if key in dic:
                    val = dic.pop(key)
                    response = f"DATA {val}"
                else:
                    response = "ERROR invalid key"

            # QUIT -> închide aplicația
            elif cmd == "QUIT":
                conn.sendall(b"inchide aplicatia\n")
                break

            # Comandă necunoscută sau eroare de sintaxă
            else:
                response = "ERROR unknown command or invalid syntax"

            # Trimitem răspunsul înapoi la client
            if cmd != "QUIT":
                conn.sendall((response + "\n").encode('utf-8'))

        except Exception as e:
            print(f"Eroare de conexiune: {e}")
            break

    conn.close()
    print(f"Client deconectat: {addr}")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Serverul a pornit pe {HOST}:{PORT}. Aștept conexiuni...")
        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)


if __name__ == "__main__":
    start_server()