#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from dataclasses import dataclass
from typing import Any

import overpassnl
from plonk import PlonkPipeline
from geoclip import GeoCLIP
from overpassnl.models.inference_t5 import predict


try:
    from PIL import Image, ExifTags
    from PIL.Image import Exif
    from torch import Tensor
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
    geoclip: Tensor
    overpass: str

class Owl:
    def __init__(self, image: str) -> None:
        self.image = image
        self.image_description: str | None = None
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
        return Result(
            metadata=self._metadata(),
            plonk=self._plonk(),
            geoclip=self._geoclip(),
            overpass=self._overpassnl(),
        )

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

    def _geoclip(self) -> None:
        """..."""
        model = GeoCLIP()
        return model.predict(self.image, top_k=5)

    def _overpassnl(self) -> str:
        """Translates the image description into an OverpassQL query with OverpassT5.

        Returns:
            str: The generated Overpass Turbo query.
        """
        # Weights: https://www.cl.uni-heidelberg.de/~rschuman/files/overpassnl/byt5-base_com08.zip
        overpassnl_model: str = os.path.join(os.path.dirname(overpassnl.__file__), "models", "outputs", "byt5-base_com08")
        self.image_description = "Cafes near the Eiffel Tower in Paris."
        return predict([self.image_description], overpassnl_model)[0]


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
