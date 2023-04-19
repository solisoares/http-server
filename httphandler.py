from enum import Enum
from html import escape as html_escape
from mimetypes import guess_type
from pathlib import Path
from urllib.parse import unquote, quote


class StatusCode(Enum):
    OK = "200 OK"
    NOT_FOUND = "404 Not Found"


class HTTPHandler:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir

    def handle_request(self, raw_request: bytes, conn):
        """Handle an HTTP request

        Args:
            raw_request (bytes): The raw request
            conn: The Server-Client TCP connection
        """
        method, path, version = raw_request.decode("utf-8").split()[:3]
        path = self.handle_path(Path(path))

        if method == "GET":
            print(f"requested path: {path}")
            self.return_response(conn, path)

        elif method != "GET":
            print("Not an HTTP GET request")
            return

        else:
            print("Not an HTTP request")
            return

    def handle_path(self, req_path: Path):
        """Retrieve a handled version of the requested path

        Args:
            req_path (Path): The requested path

        Returns:
            Path: The handled requested path
        """
        # The requested path must have no leadind slash and be unquoted.
        # - Remove leading slash to join paths correctly.
        # - The quoted url path must be unquoted to use in OS operations
        #   Example: the requested path "t%C3%A9st" is the quoted version of "tést",
        #   but to perform OS operations with this path we need it in its
        #   original form "tést", thus it is unquoted.
        req_path = Path(unquote(str(req_path).lstrip("/")))
        
        handled_path = (self.root_dir / req_path).resolve()
        return handled_path

    def return_response(self, conn, path: Path):
        header, body = "", ""

        if not path.exists():
            header = self.response_header(StatusCode.NOT_FOUND, path)
            body = self.not_found_body(path)
            conn.sendall(header + body)
        elif path.is_dir():
            header = self.response_header(StatusCode.OK, path)
            body = self.list_dir_body(path)
            conn.sendall(header + body)

        if path.is_file():
            header = self.response_header(StatusCode.OK, path)
            conn.sendall(header)
            for chunk in self.file_content(path):
                conn.sendall(chunk)

    def response_header(self, status_code: StatusCode, path: Path):
        content_type, _ = guess_type(path)
        header = f"HTTP/1.0 {status_code.value}\r\n"
        if path.is_dir():
            header += f"Content-Type: text/html; charset=utf-8\r\n"
        elif content_type:  # it is necessarily a file
            header += f"Content-Type: {content_type}; charset=utf-8\r\n"
        header += "\r\n"
        return header.encode("utf-8")

    def list_dir_body(self, directory: Path):
        """Generates HTML for a directory listing

        Args:
            directory (str): Directory to list
        """
        entries = ""  # the filepaths of a directory list

        for entry in sorted(list(directory.iterdir())):
            # Replace special characters "&", "<" and ">" to HTML-safe sequences for rendering
            escaped_entry = Path(html_escape(str(entry)))

            # The unquoted OS paths (for example "tést") must be quoted
            # to be a valid URL ("t%C3%A9st")
            quoted_entry = Path(quote(str(entry)))

            # Final slash for directories only
            final_slash = "/" if escaped_entry.is_dir() else ""

            entries += f'<li><a href="{quoted_entry.name}{final_slash}">{escaped_entry.name}{final_slash}</a></li>'

        escaped_directory = Path(html_escape(str(directory)))
        escaped_directory = (
            str(directory).split(str(self.root_dir))[-1]
            if directory != self.root_dir
            else "/"
        )

        html = f"""
            <html>
                <head>
                    <title>HTTP Server
                    </title>
                </head>
                <body>
                    <h1>Directory listing for {escaped_directory}</h1>
                    <hr>
                    <ul>{entries}</ul>
                    <hr>
                </body>
            </html>
            """
        return html.encode("utf-8")

    def not_found_body(self, path: Path):
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
        return html.encode("utf-8")

    def file_content(self, filepath: Path):
        """Yield chunk of a file"""
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(1024)
                yield chunk
                if not chunk:
                    break
