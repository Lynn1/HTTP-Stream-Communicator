
"""
https://github.com/Lynn1 update 2024.4.26 
This code implements an HTTP server that parses the request in the do_GET method, extracts the string, and generates a streaming response via a background thread append_to_queue to append to shared_queue.
Main StreamingHTTPRequestHandler HTTP server thread running, the handler will fetch string and by one character from the shared_queue streaming output to the client.
note: Queues cannot take values in the middle, while lists can take values from anywhere. Using queues ensures that access to a shared queue in a multi-thread environment is thread-safe, avoiding data inconsistencies caused by concurrent access.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import time
import queue
import urllib.parse

shared_queue = queue.Queue()  # Use queues as global shared variables for concurrent writes/reads
request_str = ""  # The request character string sent by the client
append_allowed = False  # Flag that controls whether a string is allowed to be appended to the queue
append_count = 0  # Initialize the stream build count (simulate whether the build task has completed the flag)
append_count_max = 10  # The maximum number of stream generated tasks

def append_to_queue():
    """A function run by the background thread to append a new string to the shared queue based on request_str"""
    counter = 0
    global request_str, append_allowed, append_count  # Use the global declaration to modify global variables
    while True:
        if append_allowed and append_count < append_count_max:  # Check whether the build condition is met and the build has not completed
            message = f"{request_str}: 我是新消息，我叫Message {append_count}"  # Embed the request string in the appended string (test request_str received)
            shared_queue.put(message)  # Append a string to the shared queue
            append_count += 1  # Add add count
            time.sleep(1)  # Simulate the string generation process, append a string every 1 second
        else:
            time.sleep(0.5)  # Wait when the generation conditions are not met or the generation task has been completed

class StreamingHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global request_str, append_allowed, append_count # Use the global declaration to modify global variables
        # Parse the request string from the URL of the GET request
        path_str = self.path.strip("/")
        request_str = urllib.parse.unquote(path_str)  # Decode the URL encoded string
        append_allowed = True  # The build condition is met, allowing the append string to the queue to begin
        append_count = 0  # Reset the append count to start a new build task
        shared_queue.queue.clear()  # Clear queue

        # Set the response header and status code
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8') # Ensure that the character set type is declared in the response header
        self.end_headers()
        # Send non-streaming data
        welcome_message = f"Received request string: {request_str}\nStart sending data...\n"
        self.wfile.write(welcome_message.encode('utf-8'))
        self.wfile.flush()
        # Start to stream generated data
        while True:
            try:
                # Trying to get a string from the queue
                message = shared_queue.get(timeout=3) # timeout Set the non-blocking mode here. Wait a maximum of x seconds to avoid infinite waiting
                shared_queue.task_done()  # Marks the completion of a task in the queue
                for char in message:
                    self.wfile.write(char.encode('utf-8')) # Output character by character using UTF-8 encoding
                    self.wfile.flush() # Force buffer contents to be written out
                self.wfile.write(b'\n')
                self.wfile.flush()
            except queue.Empty:
                # Processing when the queue is empty, logic can be added on demand
                # time.sleep(0.5)  # For example, wait 0.5 seconds before trying to check the queue for new content
                break  # Exit the loop and end the request

def run(server_class=HTTPServer, handler_class=StreamingHTTPRequestHandler):
    # Start the background thread to append strings continuously to the shared queue
    thread = Thread(target=append_to_queue)
    thread.daemon = True  # Set to daemon thread so that the thread ends when the main program exits
    thread.start()
    
    # Configure and start the HTTP server
    server_address = ('localhost', 8000) ###Enter the ip address of the server side
    httpd = server_class(server_address, handler_class)
    print('Starting http-server {serverIP}:{serverPort}...\n'.format(serverIP=server_address[0],serverPort=server_address[1]))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Stopping http-server.\n')
        httpd.server_close()

if __name__ == '__main__':
    run()