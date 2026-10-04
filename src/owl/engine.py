#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from dataclasses import dataclass

from plonk import PlonkPipeline

try:
    from PIL import Image
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


@dataclass
class Result:
    plonk: list[list]


def _plonk(image: str) -> list[list]:
    """This function extracts GPS coordinates from an image using the PLONK YFCC pipeline.

    Args:
        image: The path to the image to process.

    Returns:
        list[list]: A list of predicted locations.
    """
    pipeline = PlonkPipeline("nicolas-dufour/PLONK_YFCC")
    image = Image.open(image).convert("RGB")
    gps_coords = pipeline(image, batch_size=1024)
    return gps_coords
    pipeline = PlonkPipeline("nicolas-dufour/PLONK_YFCC")
    image = Image.open(image).convert("RGB")
    gps_coords = pipeline(image, batch_size=1024)
    return gps_coords


def route(image: str) -> None:
    """This function routes the image into different pipelines.

    Args:
        image: The path to the image to route into the appropriate pipeline.
    """
    result = Result
    result.plonk = _plonk(image)
    print(result.plonk)
