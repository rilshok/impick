import argparse
import hashlib
import os

import argcomplete
import uvicorn
from fastapi import FastAPI


def index():
    return "hello"


def serve(host: str, port: int):
    app = FastAPI()

    app.get("/")(index)

    uvicorn.run(app, host=host, port=port)


def _unique_port(salt: str) -> int:
    hex_dig = hashlib.sha1(salt.encode()).hexdigest()
    seed = os.getuid() + int(hex_dig, 16)
    min_, max_ = 49152, 65535
    return min_ + seed % (max_ - min_ + 1)


def start_server():
    USER_PORT = _unique_port(__file__)
    parser = argparse.ArgumentParser(description="Run the ImPick server")
    parser.add_argument("--host", default="0.0.0.0", help="host to run server on")
    parser.add_argument(
        "--port", default=USER_PORT, type=int, help="port to run server on"
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    serve(host=args.host, port=args.port)
