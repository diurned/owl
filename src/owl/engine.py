#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from dataclasses import dataclass
from typing import Any

from plonk import PlonkPipeline

try:
    from PIL import Image, ExifTags
    from PIL.Image import Exif
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
    metadata: str
    plonk: list[list]

class Owl:
    def __init__(self, image: str) -> None:
        self.image = image
        self.image_data: Exif | None = None

    @staticmethod
    def _to_decimal(dms: dict[str | int, Any], ref: dict[str | int, Any]) -> float:
        """Convert (degrees, minutes, seconds) to signed decimal degrees.

        Args:
            dms(dict[str | int, Any]): A tuple or list containing the degrees, minutes, and seconds.
            ref(dict[str | int, Any]): A string indicating the reference direction ('N'/'S' for latitude, 'E'/'W' for longitude).

        Returns:
            float: The signed decimal degree value. Negative values are returned for southern latitudes and western longitudes.
        """
        degrees, minutes, seconds = (float(x) for x in dms)
        value = degrees + minutes / 60 + seconds / 3600
        return -value if ref in ("S", "W") else value

    def locate(self) -> Result:
        """This function runs every way to locate an image and returns the result.

        Returns:
            Result: The result containing the location metadata and the predicted locations.
        """
        result = Result
        result.plonk = self._plonk()
        result.metadata = self._metadata()
        return result

    def _plonk(self) -> list[list]:
        """This function extracts GPS coordinates from an image using the PLONK YFCC pipeline.

        Returns:
            list[list]: A list of predicted locations.
        """
        pipeline = PlonkPipeline("nicolas-dufour/PLONK_YFCC")
        image = Image.open(self.image).convert("RGB")
        gps_coords = pipeline(image, batch_size=1024)
        return gps_coords

    def _metadata(self):
        """Reads image metadata to extract location metadata if it is present.

        Returns:
            str: The extracted location metadata, or an empty string if none.
        """
        image = Image.open(self.image)
        self.image_data = image.getexif()
        gps_ifd = self.image_data.get_ifd(0x8825)
        if not gps_ifd:
            return ""
        gps = {ExifTags.GPSTAGS.get(k, k): v for k, v in gps_ifd.items()}
        try:
            lat = self._to_decimal(gps["GPSLatitude"], gps["GPSLatitudeRef"])
            lon = self._to_decimal(gps["GPSLongitude"], gps["GPSLongitudeRef"])
        except KeyError:
            return str(gps)
        return f"{lat}, {lon}"


def route(image: str) -> Result:
    """This function routes the image into different pipelines.

    Args:
        image: The path to the image to route into the appropriate pipeline.

    Returns:
        Result: The result containing the location metadata and the predicted locations.
    """
    owl = Owl(image=image)
    result = owl.locate()
    return result
