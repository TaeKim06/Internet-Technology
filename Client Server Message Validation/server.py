import socket
import hashlib
import sys

def unescape(line):
    return line.replace("\\.", ".").replace("\\\\", "\\")

def compute_signature(message, key):
    hashes = hashlib.sha256()
    hashes.update(message.encode())
    hashes.update(key.encode())
    return hashes.hexdigest()

def read_newline(connection):
    data = bytearray()
    while True:
        chunk = connection.recv(1)
        if not chunk:
            break
        data.extend(chunk)
        if chunk == b'\n':
            break
    return data.decode().strip()

def server_main(listen_port, key_file):

    with open(key_file_path, 'r') as file:
        keys = [line.strip() for line in file]
        
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', listen_port))
    server_socket.listen(1)
    print("Server listening on port", listen_port)

    connection, address = server_socket.accept()
    print("Connection from", address)
    
    client_message = read_newline(connection)
    print(client_message)
    
    if client_message != "HELLO":
        print("Error: Expected Message HELLO")
        connection.close()
        return
    
    connection.sendall("260 OK\n".encode())

    counter = 0
    while True:
        client_command = read_newline(connection)
        print(client_command)
        
        if client_command == "DATA":
            lines = []
            while True:
                line = read_newline(connection)
                if line == "." or line == "\\.":
                    break
                print(line)
                lines.append(unescape(line))
            message = "\n".join(lines)
            
            
            signature = compute_signature(message, keys[counter])
            counter += 1
            connection.sendall("270 SIG\n".encode())
            connection.sendall(f"{signature}\n".encode())


        elif client_command == "QUIT":
            connection.close()
            break
        elif client_command in ["PASS", "FAIL"]:
            connection.sendall("260 OK\n".encode())
        else:
            print("Error: Invalid command from client.")
            connection.close()
            break

    server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 server.py <listen-port> <key-file>")
        sys.exit(1)
    port = int(sys.argv[1])
    key_file_path = sys.argv[2]
    server_main(port, key_file_path)