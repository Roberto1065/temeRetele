import socket
import json
import os

HOST = '127.0.0.1'
PORT = 2121
LOCAL_DIR = "local_files"

if not os.path.exists(LOCAL_DIR):
    os.makedirs(LOCAL_DIR)


def send_cmd(sock, req):
    sock.sendall(json.dumps(req).encode('utf-8'))
    res_data = sock.recv(8192)
    return json.loads(res_data.decode('utf-8'))


def list_files(sock):
    res = send_cmd(sock, {"command": "list_files"})
    if res.get("status") == "success":
        print("\nFisiere pe server:")
        for f in res.get("files", []):
            print(f" - {f}")
    else:
        print("Eroare:", res.get("message"))


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((HOST, PORT))
        except ConnectionRefusedError:
            print("Eroare: Pornește server.py mai întâi.")
            return

        print("=== Conectat la serverul FTP ===")
        user = input("Username: ")
        pwd = input("Password: ")
        res = send_cmd(sock, {"command": "login", "username": user, "password": pwd})
        print("Server:", res.get("message"))

        if res.get("status") != "success":
            return

        while True:
            print("\n--- MENIU ---")
            print("1. create_file\n2. upload\n3. rename_file\n4. read_file")
            print("5. download\n6. edit_file\n7. see_file_operation_history")
            print("8. list_files\n9. logout\n0. exit")
            opt = input("Alege optiunea: ")

            if opt == '1':
                name = input("Nume fisier: ")
                content = input("Continut: ")
                res = send_cmd(sock, {"command": "create_file", "filename": name, "content": content})
                print("Server:", res.get("message"))

            elif opt == '2':
                name = input("Nume fisier local (din local_files/): ")
                local_path = os.path.join(LOCAL_DIR, name)
                if os.path.exists(local_path):
                    with open(local_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    res = send_cmd(sock, {"command": "upload", "filename": name, "content": content})
                    print("Server:", res.get("message"))
                else:
                    print("Eroare: Fisierul nu exista in folderul local.")

            elif opt == '3':
                old_name = input("Nume fisier vechi: ")
                new_name = input("Nume fisier nou: ")
                res = send_cmd(sock, {"command": "rename_file", "old_name": old_name, "new_name": new_name})
                print("Server:", res.get("message"))

            elif opt == '4':
                list_files(sock)
                name = input("Introdu numele fisierului de citit: ")
                res = send_cmd(sock, {"command": "read_file", "filename": name})
                if res.get("status") == "success":
                    print(f"\n[Continut {name}]:\n{res.get('content')}")
                else:
                    print("Server:", res.get("message"))

            elif opt == '5':
                list_files(sock)
                name = input("Introdu fisierul pentru download: ")
                res = send_cmd(sock, {"command": "download", "filename": name})
                if res.get("status") == "success":
                    with open(os.path.join(LOCAL_DIR, name), 'w', encoding='utf-8') as f:
                        f.write(res.get("content"))
                    print(f"Succes: Fisier salvat in {LOCAL_DIR}/{name}")
                else:
                    print("Server:", res.get("message"))

            elif opt == '6':
                list_files(sock)
                name = input("Introdu fisierul de editat: ")
                content = input("Introdu noul continut: ")
                res = send_cmd(sock, {"command": "edit_file", "filename": name, "content": content})
                print("Server:", res.get("message"))

            elif opt == '7':
                list_files(sock)
                name = input("Introdu fisierul pentru istoric: ")
                res = send_cmd(sock, {"command": "see_file_operation_history", "filename": name})
                if res.get("status") == "success":
                    print(f"\n[Istoric {name}]:")
                    for line in res.get("history"):
                        print(line)
                else:
                    print("Server:", res.get("message"))

            elif opt == '8':
                list_files(sock)

            elif opt == '9':
                res = send_cmd(sock, {"command": "logout"})
                print("Server:", res.get("message"))
                break

            elif opt == '0':
                break


if __name__ == '__main__':
    main()