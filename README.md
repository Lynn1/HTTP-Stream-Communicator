# HTTP-Stream-Communicator

This is a server and client code template for sending and receiving messages through http streaming

### Run Test :

**Step1: starts the server and simulates the generated data after listening for the request**

recommand to use the latest multi-processed version :

```
# run server v1 : multi-threaded 
# python ./MTStreamQueueServer.py

# run server v2: multi-processed (latest, recommanded)
python ./MPStreamServer.py --server_ip localhost --server_port 8000 --max_gen_len 10
```

**Step2: run the client request to send request to the server and prints the server response**

 `python ./streamclient.py`

### Usage Tips:

1. Replace the *client : request_str*  with your user input information
2. Replace the server : *FakeResponser*  with your response information generation function

### 2024.4.30 update:

Use multi-process to hold the http server instead of multi-thread, communication with the fakeresponser(front process) via pipe

### 2024.4.29 update:

Exchange front and back roles: fakeresponser as front process, http monitoring service in the background

### 2024.4.26 log:

An HTTP server and client template supporting streaming communication is implemented.

The code 'MTStreamQueueServer.py' implements an HTTP server that parses the request in the do_GET method, extracts the string, and generates a streaming response via a background thread append_to_queue to append to shared_queue. Main StreamingHTTPRequestHandler HTTP server thread running, the handler will fetch string and by one character from the shared_queue streaming output to the client. note: Queues cannot take values in the middle, while lists can take values from anywhere. Using queues ensures that access to a shared queue in a multi-thread environment is thread-safe, avoiding data inconsistencies caused by concurrent access.

'streamclient.py' This code implements an HTTP client that will send a GET request to the HTTP server, containing a string (simulating user input, etc.), and then stream the server response character by character. note: To properly parse UTF-8 characters that contain Chinese characters, etc., urllib.parse.quote is urL-encoded for the request string and a buffer is used to store possible multi-byte characters in the response.
