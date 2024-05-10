
"""
https://github.com/Lynn1 update 2024.4.26 
This code implements an HTTP client that will send a GET request to the HTTP server,
The request contains a string (simulating user input),
The server response is then streamed character by character.
"""

from http.client import HTTPConnection
import urllib.parse

def request_example():
    conn = HTTPConnection("localhost", 8000, timeout=10) ###Enter the ip address of the server side
    # conn.request("GET", "/")
    # The request string contains special characters such as Chinese characters
    request_str = "醒醒，Neo" # "Wake up, Neo"
    # The string is urL-encoded using urllib.parse.quote
    encoded_request_str = urllib.parse.quote(request_str)
    # Adds an encoded string to the requested URL
    request_path = "/" + encoded_request_str
    conn.request("GET", request_path)

    response = conn.getresponse()
    print(f"Response status: {response.status}")
    print(f"Response reason: {response.reason}")
    # In order to parse UTF-8 characters correctly, a buffer is used to store possible multi-byte characters
    buffer = bytes()
    while chunk := response.read(1):
        buffer += chunk  # Adds the read bytes to the buffer
        try:
            # Attempt to decode the entire buffer contents
            text = buffer.decode('utf-8')
            print(text, end='', flush=True)
            buffer = bytes()  # Empty the buffer and wait for new content
        except UnicodeDecodeError:
            # If the decoding fails (possibly because a split multibyte character is encountered), more data is read
            continue
    conn.close()

if __name__ == '__main__':
    request_example()