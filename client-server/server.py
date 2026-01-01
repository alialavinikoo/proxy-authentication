import socket
import threading

SERVER = '0.0.0.0'
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
HEADER = 64
KEY = "HaHa1384!"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR) 

def handle_client(conn, addr):
    print(f"[new connection] {addr} connected")
    
    msg_len = conn.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg_len = int(msg_len)
        key = conn.recv(msg_len).decode(FORMAT)
        
        if key and key == KEY:
            print(f"[AUTH SUCCESS] {addr} has logged in.")
            server_send(conn, "200 OK: Auth Successful")
        else:
            print(f"[AUTH FAILED] {addr} sent wrong key: {key}")
            server_send(conn, "401 Unauthorized")
            conn.close()
            return  
    else:
        print(f"[AUTH FAILED]")
        server_send(conn, "401 Unauthorized")
        conn.close()
        return  

    
    connected = True
    while connected:
        msg_len = conn.recv(HEADER).decode(FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            msg = conn.recv(msg_len).decode(FORMAT)
            
            if msg:
                print(f"[{addr}] {msg}")
                if msg == "DISCONNECT":
                    connected = False  
                    
    conn.close()

def server_send(conn, msg):
    msg = msg.encode(FORMAT)
    msg_len = len(msg)
    len_send = str(msg_len).encode(FORMAT)
    len_send = b' ' * (HEADER - len(len_send)) + len_send
    conn.send(len_send)
    conn.send(msg)

def main():
    server.listen()
    print(f"[listening] server is listening on {SERVER}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[connections] {threading.active_count() - 1} active connections")
        

main()