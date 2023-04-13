import os
from pathlib import Path
from mimetypes import guess_type

from html import escape as html_escape

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


def handle_request(root_dir: Path, request: HTTPRequest, conn):
    """Handle an HTTP request

    Args:
        root_dir (Path): The root directory for the server
        request (HTTPRequest): The HTTP request
        conn: The Server-Client TCP connection
    """
    path = handled_requested_path(root_dir, request.path)

    if request.method == "GET":
        print(f"requested path: {path}")
        return_response(conn, path)

    elif request.method != "GET":
        print("Not an HTTP GET request")
        return

    else:
        print("Not an HTTP request")
        return


def handled_requested_path(root_dir: Path, requested: Path):
    """Retrieve a handled version of the requested path

    Correctly append the requested path to the root directory

    Args:
        root_dir (Path): The root directory for the server
        requested (Path): The requested path

    Returns:
        Path: The handled requested path
    """
    if requested == Path("/"):
        handled = root_dir
    else:
        handled = root_dir / requested
    return handled


def return_response(conn, path: Path):
    header, body = "", ""

    if not path.exists():
        header = response_header(status["not_found"], path)
        body = not_found_body(path)

    elif path.is_dir():
        header = response_header(status["ok"], path)
        body = list_dir_body(path)

    conn.sendall(header.encode("utf-8"))
    conn.sendall(body.encode("utf-8"))

    if path.is_file():
        header = response_header(status["ok"], path)
        conn.sendall(header.encode("utf-8"))
        for chunk in file_content(path):
            conn.sendall(chunk)


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
    entries = ""  # the filepaths of a directory list

    for entry in sorted(list(directory.iterdir())):
        # Replace special characters "&", "<" and ">" to HTML-safe sequences.
        escaped_entry = Path(html_escape(str(entry)))
        final_slash = "/" if escaped_entry.is_dir() else ""
        entries += f'<li><a href="{directory/entry}">{escaped_entry.name}{final_slash}</a></li>'

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


def file_content(filepath: Path):
    """Yield chunk of a file"""
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(1024)
            yield chunk
            if not chunk:
                break
