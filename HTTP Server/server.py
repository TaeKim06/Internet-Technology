import socket, json, random, datetime, hashlib, sys

def getTime():
    return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

def passHasher(password, salt):
    hashedPass = hashlib.sha256()
    hashedPass.update((password + salt).encode())
    return hashedPass.hexdigest()

def parseRequest(lines):
    parsedData = {}
    i = 1
    while i < len(lines) - 1 and lines[i] != '':
        key, info = lines[i].split(': ')
        # print(key, info)
        parsedData[key] = info
        i += 1
    return parsedData


def post(lines, userInfo, currentSessions):
    # Obtain “username” and “password” from request headers
    username = None
    password = None
    parsedData = parseRequest(lines)

    # i = 1
    # while i < len(data) - 1 and data[i] != '':
    #     key, info = data[i].split(': ')
    #     # print(key, info)
    #     parsedData[key] = info
    #     i += 1
    
    if 'username' in parsedData:
        username = parsedData.get('username')
    if 'password' in parsedData:
        password = parsedData.get('password')
    # print(username)
    # print(password)
    currentTime = getTime()
    if not username or not password:
        #Return HTTP status code “501 Not Implemented”, log with MESSAGE "LOGIN FAILED"
        print('SERVER LOG:', currentTime, 'LOGIN FAILED')
        return f'HTTP/1.0 501 Not Implemented\r\n\r\n', None
        
    
    # If “username” and “password” are valid:
    if username in userInfo:
        # print(userInfo[username])
        hashedPass, salt = userInfo[username]
        if passHasher(password, salt) == hashedPass:
            #Set a cookie called “sessionID” to a random 64-bit hexadecimal value
            sessionID = hex(random.getrandbits(64))
            #Create a session with required info for validation using the cookie
            currentSessions[sessionID] = (parsedData['username'], datetime.datetime.now())
            #Log with MESSAGE "LOGIN SUCCESSFUL: {username} : {password}"
            currentTime = getTime()
            print('SERVER LOG:', currentTime, 'LOGIN SUCCESSFUL:', username, ":", password)
            #Return HTTP 200 OK response with body “Logged in!”
            return f'HTTP/1.0 200 OK\r\nSet-Cookie: sessionID='+sessionID+'\r\n\r\nLogged in!', sessionID
        else:
            #Log with MESSAGE "LOGIN FAILED: {username} : {password}"
            print('SERVER LOG:', currentTime, 'LOGIN FAILED:', username, ":", password)
            #Return HTTP 200 OK response with body “Login failed!”
            return f'HTTP/1.0 200 OK\r\n\r\nLogin failed!', None
    else:
        #Log with MESSAGE "LOGIN FAILED: {username} : {password}"
        print('SERVER LOG:', currentTime, 'LOGIN FAILED:', username, ":", password)
        #Return HTTP 200 OK response with body “Login failed!”
        return f'HTTP/1.0 200 OK\r\n\r\nLogin failed!', None


def get(lines, userInfo, currentSessions, sessionTimeout, rootDirectory):
    #Obtain cookies from HTTP request
    parsedData = parseRequest(lines)
    splitLineOne = lines[0].split(" ")
    request = splitLineOne[1]
    # print(request)
    unSplitCookies = parsedData.get('Cookie', '')
    # print(unSplitCookies)
    if unSplitCookies:
        cookies = unSplitCookies.strip().split('=')
        # print(cookies)
    # sessionID 
    currentTime = getTime()
    #If cookies are missing return HTTP status code “401 Unauthorized”
    if not cookies:
        print(f'SERVER LOG:', currentTime, 'COOKIE INVALID: /file.txt')
        return f"HTTP/1.0 401 Unauthorized\r\n"
    # If the "sessionID" cookie exists:
    elif currentSessions.get(cookies[1]):
        # print(currentSessions.get(cookies[1]))
        # print("break\n\n")

        #Get username and timestamp information for that sessionID
        username = currentSessions.get(cookies[1])[0]
        timestamp = currentSessions.get(cookies[1])[1]
        # print(username, timestamp)

        timeHolder = datetime.datetime.now() - timestamp
        timeHolder = timeHolder.total_seconds()
        # print(timeHolder)
        #If timestamp within timeout period:
        if timeHolder < sessionTimeout:
            # print("check")
            #Update sessionID timestamp for the user to current time
            # print(currentSessions[cookies[1]])
            currentSessions[cookies[1]] = username, datetime.datetime.now()
            #If file “{root}{username}{target}” exists:
            filePath = rootDirectory + '/' + username + '/' + "file.txt"
            with open(filePath, 'r') as file:
                if request == '/file.txt':
                    #Log with MESSAGE "GET SUCCEEDED: {username} : {target}"
                    print(f'SERVER LOG:', currentTime, 'GET SUCCEEDED: '+ username +' : /file.txt')

                    contents = file.read()
                    #Return HTTP status “200 OK” with body containing the contents of the file
                    return f"HTTP/1.0 200 OK\r\n\r\n" + contents
                else:
                    #Log with MESSAGE "GET FAILED: {username} : {target}"
                    print('SERVER LOG:', currentTime, 'GET FAILED: '+ username +' : ' + request)
                    #Return HTTP status “404 NOT FOUND”
                    return f"HTTP/1.0 404 NOT FOUND\r\n"    
        else:
            #Log with MESSAGE "SESSION EXPIRED: {username} : {target}"
            print(f'SERVER LOG:', currentTime, 'SESSION EXPIRED: '+ username +' : /file.txt')
            #Return HTTP status “401 Unauthorized”
            return f"HTTP/1.0 401 Unauthorized\r\n"
    else:
        #Log with MESSAGE "COOKIE INVALID: {target}"
        print('SERVER LOG:', currentTime, 'COOKIE INVALID: /file.txt')
        #Return HTTP status “401 Unauthorized”
        return f"HTTP/1.0 401 Unauthorized\r\n"



def server_startup(IPaddress, port, accountsFile, sessionTimeout, rootDirectory):

    # print(IPaddress, port, accountsFile, sessionTimeout, rootDirectory)

    #Create and bind a TCP socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((IPaddress, port))
    #Start listening for incoming connections
    serverSocket.listen()
    # serverSocket.settimeout(sessionTimeout)
    
    #Open the accounts.json file
    with open(accountsFile) as accountsFilePtr:
        userInfo = json.load(accountsFilePtr)
    # accountsFilePtr = open(accountsFile)
    
    currentSessions = {}

    """
    SAMPLE GET REQUEST
    GET /file.txt HTTP/1.0
    Host: 127.0.0.1:8080
    User-Agent: curl/7.68.0
    Accept: */*
    Cookie: sessionID=0x68938897ef8fdfc8
    
    SAMPLE POST REQUEST
    POST / HTTP/1.0
    Host: 127.0.0.1:8080
    User-Agent: curl/7.68.0
    Accept: */*
    username: Jerry
    password: 4W61E0D8P37GLLX
    """
    counter = 0
    while True:
        #Accept an incoming connection
        connection, addr = serverSocket.accept()
        # print(connection)
        #Receive an HTTP request from the client
        data = connection.recv(4096).decode()
        # print(data.decode())

        #Extract the HTTP method, request target, and HTTP version
        lines = data.split('\r\n')
        splitLineOne = lines[0].split(" ")
        method = splitLineOne[0]
        request = splitLineOne[1]
        version = splitLineOne[2]
        # print(splitLineOne[0], splitLineOne[1], splitLineOne[2])

        if method == "POST" and request == "/":
            #Handle POST request and send response  
            response, sessionID = post(lines, userInfo, currentSessions)
            # print(response)
            # if sessionID != None:
            #     print(currentSessions[sessionID])
            
            # connection.sendall(version.encode())
            connection.sendall(response.encode())
        elif method == "GET":
            #Handle GET request and send response
            response = get(lines, userInfo, currentSessions, sessionTimeout, rootDirectory)
            connection.sendall(response.encode())
        else:
            #Send HTTP status “501 Not Implemented”
            connection.sendall('HTTP/1.0 501 Not Implemented\r\n'.encode())
            #Close the connection
        # if counter <= 12:
        #     print(counter)
        #     counter += 1
        # else: print("NULL")
        connection.close()



if __name__ == "__main__":

    """
    python3 server.py 127.0.0.1 8080 accounts.json 5 accounts/

    IP: The IP address on which the server will bind to.
    PORT: The port on which the server will listen for incoming connections.
    ACCOUNTS_FILE: A JSON file containing user accounts and their hashed passwords along with the corresponding salt.
    SESSION_TIMEOUT: The session timeout duration (in seconds).
    ROOT_DIRECTORY: The root directory containing user directories
    """

    if len(sys.argv) != 6:
        print("Usage: python3 server.py <IP> <PORT> <ACCOUNTS FILE> <SESSION TIMEOUT> <ROOT DIRECTORY>")
    elif len(sys.argv) == 6:
        IPaddress = sys.argv[1]
        port = int(sys.argv[2])
        accountsFile = sys.argv[3]
        sessionTimeout = int(sys.argv[4])
        rootDirectory = sys.argv[5]
        server_startup(IPaddress, port, accountsFile, sessionTimeout, rootDirectory)