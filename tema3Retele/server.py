import socket
import threading
import json
import os
from datetime import datetime

HOST = '127.0.0.1'
PORT = 2121
SERVER_DIR = "files"

# Creăm folderul pentru server dacă nu există
if not os.path.exists(SERVER_DIR):
    os.makedirs(SERVER_DIR)

# Dicționar pentru istoricul operațiunilor
istoric_fisiere = {}


def adauga_istoric(nume_fisier, operatiune):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if nume_fisier not in istoric_fisiere:
        istoric_fisiere[nume_fisier] = []
    istoric_fisiere[nume_fisier].append(f"{timestamp} - {operatiune}")


def handle_client(conn, addr):
    print(f"Sesiune noua FTP: {addr}")
    authenticated = False

    try:
        while True:
            data = conn.recv(8192)
            if not data:
                break

            request = json.loads(data.decode('utf-8'))
            cmd = request.get('command')

            # Login
            if cmd == 'login':
                if request.get('username') == 'student' and request.get('password') == '1234':
                    authenticated = True
                    conn.sendall(json.dumps({"status": "success", "message": "Login reusit"}).encode('utf-8'))
                else:
                    conn.sendall(json.dumps({"status": "error", "message": "Credențiale invalide"}).encode('utf-8'))
                continue

            if not authenticated:
                conn.sendall(
                    json.dumps({"status": "error", "message": "Trebuie să te autentifici mai întâi"}).encode('utf-8'))
                continue

            # Procesare comenzi
            if cmd == 'create_file':
                filename = request.get('filename')
                content = request.get('content')
                with open(os.path.join(SERVER_DIR, filename), 'w', encoding='utf-8') as f:
                    f.write(content)
                adauga_istoric(filename, "Fisier creat")
                conn.sendall(json.dumps({"status": "success", "message": f"Fisier {filename} creat"}).encode('utf-8'))

            elif cmd == 'upload':
                filename = request.get('filename')
                content = request.get('content')
                with open(os.path.join(SERVER_DIR, filename), 'w', encoding='utf-8') as f:
                    f.write(content)
                adauga_istoric(filename, "Fisier uploadat de client")
                conn.sendall(json.dumps({"status": "success", "message": "Upload reusit"}).encode('utf-8'))

            elif cmd == 'list_files':
                files = os.listdir(SERVER_DIR)
                conn.sendall(json.dumps({"status": "success", "files": files}).encode('utf-8'))

            elif cmd == "rename_file":
                old_name = request.get('old_name')
                new_name = request.get('new_name')
                old_path = os.path.join(SERVER_DIR, old_name)
                new_path = os.path.join(SERVER_DIR, new_name)
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    istoric_fisiere[new_name] = istoric_fisiere.pop(old_name, [])
                    adauga_istoric(new_name, f"Redenumit din {old_name}")
                    conn.sendall(
                        json.dumps({"status": "success", "message": f"Fisier redenumit in {new_name}"}).encode('utf-8'))
                else:
                    conn.sendall(json.dumps({"status": "error", "message": "Fisierul nu exista"}).encode('utf-8'))

            elif cmd == "read_file":
                filename = request.get('filename')
                filepath = os.path.join(SERVER_DIR, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    adauga_istoric(filename, "Continut citit")
                    conn.sendall(json.dumps({"status": "success", "content": content}).encode('utf-8'))
                else:
                    conn.sendall(json.dumps({"status": "error", "message": "Fisier lipsa"}).encode('utf-8'))

            elif cmd == "download":
                filename = request.get('filename')
                filepath = os.path.join(SERVER_DIR, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    adauga_istoric(filename, "Descarcat de client")
                    conn.sendall(json.dumps({"status": "success", "content": content}).encode('utf-8'))
                else:
                    conn.sendall(json.dumps({"status": "error", "message": "Fisier lipsa"}).encode('utf-8'))

            elif cmd == "edit_file":
                filename = request.get('filename')
                content = request.get('content')
                filepath = os.path.join(SERVER_DIR, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    adauga_istoric(filename, "Continut editat")
                    conn.sendall(json.dumps({"status": "success", "message": "Fisier actualizat"}).encode('utf-8'))
                else:
                    conn.sendall(json.dumps({"status": "error", "message": "Fisier lipsa"}).encode('utf-8'))

            elif cmd == "see_file_operation_history":
                filename = request.get('filename')
                if filename in istoric_fisiere:
                    conn.sendall(
                        json.dumps({"status": "success", "history": istoric_fisiere[filename]}).encode('utf-8'))
                else:
                    conn.sendall(json.dumps({"status": "error", "message": "Nu exista istoric"}).encode('utf-8'))

            elif cmd == 'logout':
                authenticated = False
                conn.sendall(json.dumps({"status": "success", "message": "Logout reusit"}).encode('utf-8'))
                break

            else:
                conn.sendall(json.dumps({"status": "error", "message": "Comandă necunoscută"}).encode('utf-8'))

    except Exception as e:
        pass
    finally:
        print(f"Client deconectat: {addr}")
        conn.close()


def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server FTP pornit pe {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == '__main__':
    run_server()