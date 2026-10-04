#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from owl.engine import route

try:
    import typer
except ModuleNotFoundError as e:
    print(
        f"Mandatory dependencies are missing:\n{e}"
        "Please install them with python3 -m pip install --no-cache-dir --upgrade -r requirements.txt"
    )
    exit(1)
except ImportError as e:
    print(f"An error occurred while loading the dependencies!\nDetails:\n{e}")
    exit(1)
except KeyboardInterrupt:
    exit(1)

app = typer.Typer(help="Artificial Intelligence Geospatial Intelligence Tool")


@app.command(help="Locate an image")
def locate(
    image: str = typer.Option(None, "--image", "-i", help="path to image to locate"),
) -> None:
    """..."""
    if os.path.exists(image) and os.path.isfile(image):
        result = route(image)
        typer.echo(result.plonk, color=True)
        typer.echo(result.metadata, color=True)
    else:
        typer.echo("Path does not exists or is not a file.", err=True)
