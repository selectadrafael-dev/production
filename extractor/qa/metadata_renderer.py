from PIL import ImageDraw

from .colors import *


class MetadataRenderer:

    def render(

        self,

        draw,

        metadata

    ):

        for block in metadata:

            box = block["bbox"]

            x = box["x"]

            y = box["y"]

            w = box["width"]

            h = box["height"]

            draw.rectangle(

                (

                    x,

                    y,

                    x+w,

                    y+h

                ),

                outline=BLUE,

                width=2

            )

            draw.text(

                (

                    x,

                    y-12

                ),

                block["type"],

                fill=BLUE

            )


metadata_renderer = MetadataRenderer()