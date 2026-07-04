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

            #
            # Draw candidate rectangle
            #

            draw.rectangle(

                (

                    x,

                    y,

                    x + w,

                    y + h

                ),

                outline=RED,

                width=4

            )

            #
            # Candidate Role
            #

            role = candidate.get(

                "role",

                ""

            )

            if role == "parent":

                role = "[P]"

            elif role == "variant":

                role = "[V]"

            elif role == "detail":

                role = "[D]"

            elif role == "lifestyle":

                role = "[L]"

            else:

                role = ""

            #
            # Candidate Label
            #

            family = candidate.get(

                "family",

                ""

            )

            role = candidate.get(

                "role",

                ""

            )

            label = candidate["id"]

            if family:

                label += f" {family}"

            if role == "parent":

                label += " [P]"

            elif role == "variant":

                label += " [V]"

            elif role == "detail":

                label += " [D]"

            elif role == "lifestyle":

                label += " [L]"

            if role:

                label += " " + role

            draw.text(

                (

                    x,

                    y - 18

                ),

                label,

                fill=RED

            )


candidate_renderer = CandidateRenderer()