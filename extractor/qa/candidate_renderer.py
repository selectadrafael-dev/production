from PIL import ImageDraw

from .colors import *


class CandidateRenderer:

    def render(

        self,

        draw,

        candidates

    ):

        for candidate in candidates:

            bbox = candidate["bbox"]

            x = bbox["x"]

            y = bbox["y"]

            w = bbox["width"]

            h = bbox["height"]

            draw.rectangle(

                (

                    x,

                    y,

                    x+w,

                    y+h

                ),

                outline=RED,

                width=4

            )

            draw.text(

                (

                    x,

                    y-18

                ),

                candidate["id"],

                fill=RED

            )


candidate_renderer = CandidateRenderer()