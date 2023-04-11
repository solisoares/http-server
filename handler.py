import os
from collections import namedtuple


# HTTP Request
# Contains:
#     METHOD: GET, POST...
#     PATH: filepath to directory, text file, binaries ...
#     VERSION: HTTP version
HTTPRequest = namedtuple("HTTPRequest", ["method", "path", "version"])


def parse_http_request_from_data(data):
    """Parse the first line of an http request from received data

    Args:
        data (binary str): data sent from client

    Returns:
        HTTPRequest: The request with http method, requested path and HTTP version
    """
    request = HTTPRequest(*data.decode("utf-8").split()[:3])
    return request


def handle_request(request: HTTPRequest, conn):
    """Handle an HTTP request

    Args:
        request (HTTPRequest): The HTTP request
        conn: The Server-Client TCP connection
    """
    if request.method == "GET":
        # print(request.method, request.path, request.version)
        print(f"requested path: {request.path}")
        return_response(conn, request.path)

    elif request.method != "GET":
        print("Not an HTTP GET request")
        return

    else:
        print("Not an HTTP request")
        return


def return_response(conn, path):
    header, body = "", ""
    if os.path.isdir(path):
        os.chdir(path)
        header = 'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n'
        body = html_for_listing_directory(path)
        
    elif os.path.isfile(path):
        os.chdir(os.path.dirname(path))
        header = ''
        body = text_file_content(path)

    response = header + body
    conn.sendall(response.encode('utf-8'))


def html_for_listing_directory(directory):
    """Generates HTML for a directory listing

    Args:
        directory (str): Directory to list
    """
    entries = ""

    for entry in sorted(os.listdir(directory)):
        _entry = directory + "/" + entry if directory != "/" else directory + entry
        entries += f'<li><a href="{_entry}">{entry}/</a></li>'

    html = f'''
<html>
    <head>
        <title>HTTP Server
        </title>
    </head>
    <body>
        <h1>Directory listing for {directory}</h1>
        <hr>
        <ul>{entries}</ul>
        <hr>
    </body>
</html>
'''
    return html


def text_file_content(file):
    with open(file, "r") as f:
        content = f.read()
    return content
