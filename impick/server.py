import argparse
import hashlib
import os
from pathlib import Path

import argcomplete
import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "html"))


def parse_image_dir(root: Path):
    for group_dir in root.iterdir():
        if not group_dir.is_dir():
            continue
        paths = (p.relative_to(root) for p in group_dir.glob("*.jpg"))

        yield group_dir.name, list(map(str, paths))


def get_index(image_groups):
    def index(request: Request):
        iterator = iter(image_groups)
        group_name = next(iterator)
        images_paths = image_groups[group_name]
        print(group_name, images_paths)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "group_name": group_name,
                "images_paths": images_paths,
                "group_index": 1,
                "groups_total": len(image_groups),
            },
        )

    return index


def select_image(
    request: Request, group_name: str = Query(...), image_name: str = Query(...)
):
    print(f"Selected Group: {group_name}")
    print(f"Selected Image: {image_name}")
    return RedirectResponse(url="/")


def serve(host: str, port: int, root: Path):
    app = FastAPI()

    image_groups = dict(parse_image_dir(root))
    # print(image_groups)

    app.mount("/images", StaticFiles(directory=str(root)), name="images")

    app.get("/")(get_index(image_groups))
    app.get("/select_image")(select_image)

    uvicorn.run(app, host=host, port=port)


def _unique_port(salt: str) -> int:
    hex_dig = hashlib.sha1(salt.encode()).hexdigest()
    seed = os.getuid() + int(hex_dig, 16)
    min_, max_ = 49152, 65535
    return min_ + seed % (max_ - min_ + 1)


def start_server():
    USER_PORT = _unique_port(__file__)
    parser = argparse.ArgumentParser(
        description="Run the ImPick server",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="host to run server on",
    )
    parser.add_argument(
        "--port",
        default=USER_PORT,
        type=int,
        help="port to run server on",
    )
    parser.add_argument(
        "--root",
        default=os.getcwd(),
        help="root directory with image groups",
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    serve(
        host=args.host,
        port=args.port,
        root=Path(args.root).expanduser().absolute(),
    )
