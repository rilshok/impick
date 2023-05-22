import argparse
import csv
import hashlib
import os
import random
from pathlib import Path
from typing import Dict, Iterator, List, Literal, Optional, Tuple

import argcomplete
import pandas as pd
import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory=str(Path(__file__).parent / "html"))


def parse_image_dir(root: Path) -> Iterator[Tuple[str, List[str]]]:
    for group_dir in root.iterdir():
        if not group_dir.is_dir():
            continue
        paths = [p.relative_to(root) for p in group_dir.glob("*.jpg")]

        yield group_dir.name, list(map(str, paths))


def write_to_csv(file_path: Path, path: str, group: str, file: str):
    file_exists = file_path.exists()
    with open(file_path, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["path", "group", "file"])
        writer.writerow([path, group, file])


def index(
    image_groups: Dict[str, List[str]],
    report: Path,
    mode: Literal["sequential", "individual"],
):
    groups = set(image_groups.keys())

    def inner(request: Request, path: Optional[str] = None):
        if report.exists():
            frame = pd.read_csv(str(report))
            if mode == "individual":
                frame = frame[frame["path"] == path]
            elif mode == "sequential":
                pass
            else:
                raise ValueError(f"Invalid mode: {mode}")
            choices = list(groups - set(frame["group"].astype(str)))
            if not choices:
                return RedirectResponse(url="/completed")
            index = len(frame) + 1
            group_name = random.choice(choices)
        else:
            index = 1
            group_name = random.choice(list(groups))

        images_paths = image_groups[group_name]

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "group_name": group_name,
                "images_paths": images_paths,
                "group_index": index,
                "groups_total": len(image_groups),
                "path": path,
            },
        )

    return inner


def selector(report: Path):
    if not report.exists():
        if not report.parent.exists():
            raise FileNotFoundError("Report parent directory does not exist")

    def inner(
        request: Request,
        group_name: str = Query(...),
        image_name: str = Query(...),
        path: str = Query(),
    ):
        image_name_split = image_name.split("/", 1)
        if image_name_split[0] != group_name:
            raise ValueError("Image name does not match group name")
        selected_image = image_name_split[1]
        write_to_csv(file_path=report, path=path, group=group_name, file=selected_image)
        return RedirectResponse(url=f"/{path}")

    return inner


def completed(total_cases: int):
    def inner(request: Request):
        return templates.TemplateResponse(
            "completed.html",
            {
                "request": request,
                "total_cases": total_cases,
            },
        )

    return inner


def serve(
    host: str,
    port: int,
    images: Path,
    report: Path,
    mode: Literal["sequential", "individual"],
):
    if not images.exists():
        raise FileNotFoundError("Images directory does not exist")

    app = FastAPI()

    image_groups = dict(parse_image_dir(images))

    app.mount("/images", StaticFiles(directory=str(images)), name="images")
    app.get("/select_image")(selector(report))
    app.get("/completed")(completed(len(image_groups)))
    app.get("/{path}")(index(image_groups, report, mode=mode))
    app.get("/")(lambda: RedirectResponse(url="/anonym"))

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
        "--images-root",
        default=os.getcwd(),
        help="root directory with image groups",
    )
    parser.add_argument(
        "--report-file",
        default="report.csv",
        help="path to the CSV file for reporting",
    )
    parser.add_argument(
        "--mode",
        choices=["sequential", "individual"],
        default="sequential",
        help="Mode for viewing groups of images: 'sequential' or 'individual'. Default is 'sequential'.",
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    serve(
        host=args.host,
        port=args.port,
        images=Path(args.images_root).expanduser().absolute(),
        report=Path(args.report_file).expanduser().absolute(),
        mode=args.mode,
    )
