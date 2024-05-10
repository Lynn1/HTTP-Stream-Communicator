# HTTP-StreamQueue

This is a server and client code template for sending and receiving messages through http streaming

### Run Test :

The test starts the server and simulates the generated data after listening for the request

 `python ./MTStreamQueueServer.py`

The test sends the client request and prints the server response

 `python ./streamclient.py`

### Usage Tips:

1. Replace the *client request sending string* with your user input information
2. Replace the *line of server generated data* with your response information generation function

### 2024.4.26 log:

An HTTP server and client template supporting streaming communication is implemented.

The code 'MTStreamQueueServer.py' implements an HTTP server that parses the request in the do_GET method, extracts the string, and generates a streaming response via a background thread append_to_queue to append to shared_queue. Main StreamingHTTPRequestHandler HTTP server thread running, the handler will fetch string and by one character from the shared_queue streaming output to the client. note: Queues cannot take values in the middle, while lists can take values from anywhere. Using queues ensures that access to a shared queue in a multi-thread environment is thread-safe, avoiding data inconsistencies caused by concurrent access.

'streamclient.py' This code implements an HTTP client that will send a GET request to the HTTP server, containing a string (simulating user input, etc.), and then stream the server response character by character. note: To properly parse UTF-8 characters that contain Chinese characters, etc., urllib.parse.quote is urL-encoded for the request string and a buffer is used to store possible multi-byte characters in the response.
