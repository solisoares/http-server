import argparse
import os
import signal
import socket
import sys
from pathlib import Path

from httphandler import HTTPHandler


DIR_CALLED = Path(os.getcwd())
HOST = "127.0.0.1"  # localhost
PORT = 65432


def serve(*, root_dir, host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    with server_socket:
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Serving HTTP on {host} port {port} (http://{host}:{port}/) ...")

        handler = HTTPHandler(root_dir)
        while True:
            conn, addr = server_socket.accept()  # (host, port)
            with conn:
                raw_request = conn.recv(1024)
                if not raw_request:
                    print("Received empty data. Awaiting new connection...")
                    continue
                handler.handle_request(raw_request, conn)


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
    parser.add_argument(
        "--dir",
        type=str,
        default=DIR_CALLED,
        help="specify root directory [default: the directory you're at right now]",
    )
    return parser.parse_args()


def signal_handler(signal, frame):
    print("\nExiting...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    args = parse_args()
    serve(root_dir=Path(args.dir), host=args.host, port=args.port)
