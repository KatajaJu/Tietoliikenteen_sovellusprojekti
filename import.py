import socket

SERVER_IP = "172.20.241.9"
SERVER_PORT = 20000
GROUPID = 1

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10)
        s.connect((SERVER_IP, SERVER_PORT))
        s.sendall(f"{GROUPID}\n".encode("utf-8"))
        received_data = b""

        while True:
            data = s.recv(4096)
            if not data:
                break
            received_data += data

    with open("datat.txt", "wb") as file:
        file.write(received_data)

    print("Data tallennettu tiedostoon datat.txt")
    print(received_data.decode("utf-8"))

except Exception as e:
    print("Virhe:", e)
