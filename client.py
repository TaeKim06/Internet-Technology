import socket
import sys

def unescape(line):
    return line.replace("\\.", ".").replace("\\\\", "\\")

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

def client_main(server_name, server_port, message_filename, signature_filename):

    with open(message_filename, 'r') as file:
        messages = []
        while True:
            length_str = file.readline().strip()
            if not length_str:
                break
            length = int(length_str)
            message = file.read(length)
            messages.append(message)

    with open(signature_filename, 'r') as file:
        signatures = [line.strip() for line in file]

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_name, server_port))

    # Send the HELLO message
    client_socket.sendall("HELLO\n".encode())
    response = read_newline(client_socket)
    print(response)
    
    if response.strip() != "260 OK":
        print("Error: Invalid response from server.")
        client_socket.close()
        return

    for message, expected_signature in zip(messages, signatures):
        # Send Data command
        client_socket.sendall("DATA\n".encode())
        
        # Send message
        for line in message.splitlines():
            client_socket.sendall(f"{line}\n".encode())
        client_socket.sendall(".\n".encode())
        
        response = read_newline(client_socket)
        if response.strip() != "270 SIG":
            print("Error: Expected 270 SIG")
            client_socket.close()
            return

        server_signature = read_newline(client_socket)
        print(server_signature)

        if server_signature == expected_signature:
            client_socket.sendall("PASS\n".encode())
        else:
            client_socket.sendall("FAIL\n".encode())

        response = read_newline(client_socket)
        print(response)
        if response.strip() != "260 OK":
            print("Error: Expected 260 OK")
            client_socket.close()
            return
        

    client_socket.sendall("QUIT\n".encode())
    client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 client.py <server-name> <server-port> <message-filename> <signature-filename>")
        sys.exit(1)
    server_name = sys.argv[1]
    port = int(sys.argv[2])
    message_file_path = sys.argv[3]
    signature_file_path = sys.argv[4]
    client_main(server_name, port, message_file_path, signature_file_path)