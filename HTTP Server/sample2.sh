# Set your server IP and port
SERVER_IP="Localhost"
SERVER_PORT="8080"

# Variables for storing session cookies
SESSION_COOKIE=""

# Common curl options for HTTP/1.0 and connection close
CURL_OPTIONS="--http1.0 --connect-timeout 5 --max-time 10 --fail --silent"

# Create a results file
RESULTS_FILE="test_results.txt"
echo "Test Results" > "$RESULTS_FILE"
echo "=============" >> "$RESULTS_FILE"

# 1. No Username (POST at the root)
result=$(curl -i -X POST -H "password: test" "http://${SERVER_IP}:${SERVER_PORT}/")
echo "1. No Username (POST at the root)" >> "$RESULTS_FILE"
echo "$result" >> "$RESULTS_FILE"

# 2. No Password (POST at the root)
result=$(curl -i -X POST -H "username: test" "http://${SERVER_IP}:${SERVER_PORT}/")
echo "2. No Password (POST at the root)" >> "$RESULTS_FILE"
echo "$result" >> "$RESULTS_FILE"

# 3. Username incorrect (POST at the root)
result=$(curl -i -X POST -H "username: IncorrectUser" -H "password: test" "http://${SERVER_IP}:${SERVER_PORT}/")
echo "3. Username incorrect (POST at the root)" >> "$RESULTS_FILE"
echo "$result" >> "$RESULTS_FILE"

# 4. Password incorrect (POST at the root)
result=$(curl -i -X POST -H "username: Jerry" -H "password: wrongPassword" "http://${SERVER_IP}:${SERVER_PORT}/")
echo "4. Password incorrect (POST at the root)" >> "$RESULTS_FILE"
echo "$result" >> "$RESULTS_FILE"

# 5. Username (1st username) correct/password correct (POST at the root)
SESSION_COOKIE=$(curl -i -X POST -H "username: Jerry" -H "password: 4W61E0D8P37GLLX" "http://${SERVER_IP}:${SERVER_PORT}/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)
echo "5. Correct User and Pass \\nCookie (sessionID) for user: $SESSION_COOKIE" >> "$RESULTS_FILE"

# 6. Username (1st username) correct/password correct (POST at the root) -> Generate a new cookie
SESSION_COOKIE=$(curl -i -X POST -H "username: Jerry" -H "password: 4W61E0D8P37GLLX" "http://${SERVER_IP}:${SERVER_PORT}/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)
echo "6. New session \\nNew Cookie (sessionID) for user: $SESSION_COOKIE" >> "$RESULTS_FILE"

# 7. Invalid cookie (GET)
result=$(curl $CURL_OPTIONS -i -v -X GET -H "Cookie: sessionID=invalid_cookie" "http://${SERVER_IP}:${SERVER_PORT}/file.txt")
echo "7. Invalid cookie (GET)" >> "$RESULTS_FILE"
echo "$result" >> "$RESULTS_FILE"

# First, get the valid session cookie from a successful login
SESSION_COOKIE=$(curl -i -X POST -H "username: Jerry" -H "password: 4W61E0D8P37GLLX" "http://127.0.0.1:8080/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2)
# Then, use the session cookie to GET a file
result=$(curl $CURL_OPTIONS -i -v -X GET -H "Cookie: $SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt")
echo "8. GET file with valid session cookie" >> "$RESULTS_FILE"
echo "$result" >> "$RESULTS_FILE"

SESSION_COOKIE=$(curl -i -v -X POST -H "username: Richard" -H "password: 3TQI8TB39DFIMI6" "http://${SERVER_IP}:${SERVER_PORT}/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)
echo "\\nCookie (sessionID) for user: $SESSION_COOKIE" >> "$RESULTS_FILE"

result=$(curl $CURL_OPTIONS -i -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt")
echo "9. GET file with valid session cookie" >> "$RESULTS_FILE"
echo "$result" >> "$RESULTS_FILE"

result=$(curl $CURL_OPTIONS -i -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/filer.txt")
echo "10. GET file that does not exist" >> "$RESULTS_FILE"
echo "$result" >> "$RESULTS_FILE"

sleep 6

result=$(curl $CURL_OPTIONS -i -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt")
echo "11. GET file with valid session cookie after sleep" >> "$RESULTS_FILE"
echo "$result" >> "$RESULTS_FILE"

# Display the results
cat "$RESULTS_FILE"