import socket
import threading
import select


PORT = 5050
SERVER = '0.0.0.0'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
# simultaneous connections
CLIENTS = 10
# chuncks of 1 kilobyte
BUCKET = 1024
# admin:1234
AUTH_KEY = "YWRtaW46MTIzNA=="


proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy.bind(ADDR)

def start_tunnel(client_socket, remote_socket):
    """
    Shovels data blindly between two sockets.
    Terminates when either side closes the connection.
    """
    sockets = [client_socket, remote_socket]
    
    while True:
        readable, _, _ = select.select(sockets, [], [], 10)
        
        if not readable:
            break
            
        for sock in readable:
            try:
                data = sock.recv(4096)
                if not data:
                    return
                
                if sock is client_socket:
                    remote_socket.sendall(data)
                else:
                    client_socket.sendall(data)
            except:
                return

def handle_client(conn, addr):
    request = b''
    
    conn.settimeout(0.1)
    
    while True:
        try:
            data = conn.recv(BUCKET)
            request += data
            
        except:
            break
        
    if request:
        try:
            method, host, port, auth_token = parse_request(request)
            print(f"[{addr[0]}] Target: {host}:{port} | Auth Provided: {auth_token}")
            
            if auth_token == AUTH_KEY:
                print(f"[{addr[0]}] Access Granted! Tunneling to {host}:{port}")

                conn.settimeout(None) 

                try:
                    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    remote_socket.connect((host, port))

                    if method == "CONNECT":
                        conn.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                        start_tunnel(conn, remote_socket)

                    else:
                        remote_socket.sendall(request)
                        start_tunnel(conn, remote_socket)

                    remote_socket.close()

                except Exception as e:
                    print(f"[{addr[0]}] Forwarding Error: {e}")
            else:
                print(f"[{addr[0]}] Access Denied. Sending 407...")
                send_407(conn)
                
        except Exception as e:
            print(f"Error: {e}")
            conn.close()
            return
    
    conn.close()
        
def send_407(conn):
    response = (
        "HTTP/1.1 407 Proxy Authentication Required\r\n"
        "Proxy-Authenticate: Basic realm=\"My Secret Proxy\"\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    conn.send(response.encode(FORMAT))
        
def parse_request(request):
    request_line = request.decode(FORMAT).split('\r\n')[0]
    
    words = request_line.split(' ')
    method = words[0]
    
    # HTTPS
    if method == "CONNECT":
        host, port = words[1].split(':')
    # HTTP
    else:
        port = 80
        host = words[1].split('/')[2]
        
        if ':' in host:
            host, port_str = host.split(':')
            port = int(port_str)
        else:
            port = 80
            
    headers = request.decode(FORMAT).split("\r\n")
    
    auth_token = None
    for header in headers:
        if ':' in header:
            if header.split(':')[0].lower() == "proxy-authorization":
                try:
                    auth_token = header.split(':')[1].strip().split()[1]
                except IndexError:
                    pass 
        
    return method, host, int(port), auth_token

def main():
    print(f"[PROXY SERVER] listening on {SERVER}:{PORT}")
    proxy.listen(CLIENTS)
    while True:
        conn, addr = proxy.accept()
        print(f"[PROXY SERVER] new connection from {addr[0]}:{addr[1]}")
        
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()
        print(f"[PROXY SERVER] {threading.active_count() - 1} active connections")

if __name__ == "__main__":
    main()