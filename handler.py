import os
from pathlib import Path
from mimetypes import guess_type

from collections import namedtuple


status = {"ok": "200 OK", "not_found": "404 Not Found"}


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
    method, path, version = data.decode("utf-8").split()[:3]
    request = HTTPRequest(method, Path(path), version)
    return request


def handle_request(request: HTTPRequest, conn):
    """Handle an HTTP request

    Args:
        request (HTTPRequest): The HTTP request
        conn: The Server-Client TCP connection
    """
    if request.method == "GET":
        print(f"requested path: {request.path}")
        return_response(conn, request.path)

    elif request.method != "GET":
        print("Not an HTTP GET request")
        return

    else:
        print("Not an HTTP request")
        return


def return_response(conn, path: Path):
    header, body = "", ""

    if not path.exists():
        header = response_header(status["not_found"], path)
        body = not_found_body(path)

    elif path.is_dir():
        os.chdir(path)
        header = response_header(status["ok"], path)
        body = list_dir_body(path)

    conn.sendall(header.encode("utf-8"))
    conn.sendall(body.encode("utf-8"))

    if path.is_file():
        os.chdir(os.path.dirname(path))
        header = response_header(status["ok"], path)
        conn.sendall(header.encode("utf-8"))
        for chunk in text_file_body(path):
            conn.sendall(chunk.encode("utf-8"))


def response_header(status, path: Path):
    content_type, _ = guess_type(path)
    header = f"HTTP/1.0 {status}\r\n"
    if content_type:
        header += f"Content-Type: {content_type}; charset=utf-8\r\n"
    header += "\r\n"
    return header


def list_dir_body(directory: Path):
    """Generates HTML for a directory listing

    Args:
        directory (str): Directory to list
    """
    entries = ""

    for entry in sorted(list(directory.iterdir())):
        entries += f'<li><a href="{directory/entry}">{entry.name}/</a></li>'

    html = f"""
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
"""
    return html


def not_found_body(path: Path):
    """Generates HTML for path not found"""
    html = f"""
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: 404</p>
        <p>Message: Could not find the requested path: {path}</p>
    </body>
</html>
"""
    return html


def text_file_body(filepath: Path):
    """Yield chunk of a text file"""
    with open(filepath, "r") as f:
        while True:
            chunk = f.read(1024)
            yield chunk
            if not chunk:
                break
