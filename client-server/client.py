import socket

SERVER = '192.168.1.2'
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
HEADER = 64
KEY = "HaHa1384!"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    msg = msg.encode(FORMAT)
    msg_len = len(msg)
    len_send = str(msg_len).encode(FORMAT) 
    len_send = b' ' * (HEADER - len(len_send)) + len_send
    client.send(len_send)
    client.send(msg)
    
def receive():
    msg_len = client.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg_len = int(msg_len)
        msg = client.recv(msg_len).decode(FORMAT)
        return msg
    return None
    
print("attempting to log in")
send("KEY")
auth = receive()
print(f"Server: {auth}")

if auth == "200 OK: Auth Successful":
    print("Login Verified! Sending data...")
    send("Hello Server, I am authenticated!")
    send("DISCONNECT")
else:
    print("Login Failed. Exiting.")
    client.close()    
    