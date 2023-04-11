# http server

import socket
import os
import argparse

from handler import (
    parse_http_request_from_data,
    handle_request,
)

HOST = "127.0.0.1"  # localhost
PORT = 65432


def serve(host=HOST, port=PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    with server_socket:
        bind(server_socket, host, port)
        server_socket.listen()

        print(f"Serving HTTP on {HOST} port {PORT} (http://{host}:{port}/) ...")

        while True:
            conn, addr = server_socket.accept()  # (host, port)
            with conn:
                data = conn.recv(1024)
                if not data:
                    print("Received empty data. Awaiting new connection...")
                    continue
                request = parse_http_request_from_data(data)
                handle_request(request, conn)


def bind(server_socket, host, port):
    server_socket.bind((host, port))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        type=str,
        default=HOST,
        help="specify alternate host [default: localhost (127.0.0.1)]",
    )
    parser.add_argument(
        "--port", type=int, default=PORT, help="specify alternate port [default: 65432]"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    serve(args.host, args.port)
