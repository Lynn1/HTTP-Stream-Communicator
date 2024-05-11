
"""
https://github.com/Lynn1 update 2024.4.30
This code starts a generate_messages main process that communicates with the http_server child process via pipe,
After the generate_messages process receives the request string, it calls the fakeresponser stream to generate the response string and sends it to the http_server process via pipe stream.
The http_server subprocess listens for external client HTTP requests, parses the client request string, and passes it to the generate_messages process for a response.

Run Example:
python ./MPStreamServer.py --server_ip localhost --server_port 8000 --max_gen_len 10
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import multiprocessing
import time
import queue
import urllib.parse
import fire
import os

class FakeResponser:
    def __init__(self,
                 max_gen_len:int=10):
        self.max_gen_len = max_gen_len

    def __call__(self, user_query):
        for i in range(self.max_gen_len):
            time.sleep(1) # Simulate the seg generation process, append one seg every 1 second
            seg = f"{user_query}: 我是新消息，我叫Message {i}. "
            yield seg
        yield "<end>"


localrank = 0
parent_conn1 = None
child_conn1 = None


def generate_messages(fakeresponser,recv_conn):
    """fakeresponser sends a response message to the child process according to request_str """
    request_str = ""
    while True:
        request_str = recv_conn.recv() # Receive the request string from the communication subprocess
        print(f"{localrank}: responser Received request: {request_str}")
        if request_str:  # Check if the build condition is met and the build is not complete
            print(f"{localrank}: responser start generate...")
            start_time = time.time()
            message = ""
            for seg in fakeresponser(request_str): # Stream generated string
                print(f"{localrank}: responser yield: {seg}")
                recv_conn.send(seg) # Sends the generated string to the communication child process
                message +=seg
            print(f"{localrank}: responser finish generate respond: \n{message} \ntime cost: {time.time() - start_time:.2f} seconds")
            request_str = ""
        else:
            time.sleep(1)  # Wait when the build condition is not met or the build task has been completed


class StreamingHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global child_conn1
        if not child_conn1:
            print("child_conn1 is None")
            return
        self.send_conn = child_conn1
        # Parse the request string from the URL of the GET request
        path_str = self.path.strip("/")
        request_str = urllib.parse.unquote(path_str)  # Decode the URL encoded string
        self.send_conn.send(request_str)  # Sends the request string to the background thread
        print(f"{localrank}: http Received request: {request_str}")


        # Set the response header and status code
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8') # Ensure that the character set type is declared in the response header
        self.end_headers()
        # Start streaming communication
        while True:
            if self.send_conn.poll():
                seg = self.send_conn.recv() 
                seg_str = f"{seg}"  #The string fetched from the main process fakeresponser
                if seg_str == '<end>': # End of the stream
                    self.wfile.write(b'\n')
                    self.wfile.flush()
                    break  
                for char in seg_str: 
                    self.wfile.write(char.encode('utf-8')) # Output character by character using UTF-8 encoding
                    self.wfile.flush() # Force buffer contents to be written out


def http_server(
        send_conn,
        server_ip:str="localhost",
        server_port:int=8080,
        server_class=HTTPServer, 
        handler_class=StreamingHTTPRequestHandler
):
    global child_conn1  # Use global declarations to modify global variables
    child_conn1 = send_conn
    httpd = server_class((server_ip, server_port), handler_class)

    print(f'Starting http-server {server_ip}:{server_port}...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Stopping http-server.\n')
        httpd.server_close()


def main(
        server_ip:str="localhost",
        server_port:int=8000,
        max_gen_len:int=10
):
    # build & load fakeresponser
    fakeresponser = FakeResponser(max_gen_len=max_gen_len)
    
    # Start background threads, configure and start HTTP server
    global localrank
    localrank = int(os.environ.get("LOCAL_RANK", 0))
    server_IP = server_ip
    server_Port = server_port+localrank
    # if localrank < 1:
    print(f"Main {localrank}: Start HTTP server on {server_IP}:{server_Port}...")

    
    global parent_conn1, child_conn1
    parent_conn1, child_conn1 = multiprocessing.Pipe()
    http_process = multiprocessing.Process(target=http_server, args=(child_conn1,server_IP,server_Port,))
    http_process.daemon = True
    http_process.start()

    # call responser
    generate_messages(fakeresponser,parent_conn1)
   

if __name__ == '__main__':
    fire.Fire(main)


