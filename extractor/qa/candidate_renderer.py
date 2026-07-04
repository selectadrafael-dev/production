from .colors import *


class CandidateRenderer:

    # =====================================
    # Draw dashed rectangle
    # =====================================

    def _draw_dashed_rectangle(

        self,

        draw,

        x,

        y,

        w,

        h,

        colour,

        dash=10,

        gap=6,

        width=3

    ):

        #
        # Top
        #

        i = x

        while i < x + w:

            draw.line(

                (

                    i,

                    y,

                    min(i + dash, x + w),

                    y

                ),

                fill=colour,

                width=width

            )

            i += dash + gap

        #
        # Bottom
        #

        i = x

        while i < x + w:

            draw.line(

                (

                    i,

                    y + h,

                    min(i + dash, x + w),

                    y + h

                ),

                fill=colour,

                width=width

            )

            i += dash + gap

        #
        # Left
        #

        i = y

        while i < y + h:

            draw.line(

                (

                    x,

                    i,

                    x,

                    min(i + dash, y + h)

                ),

                fill=colour,

                width=width

            )

            i += dash + gap

        #
        # Right
        #

        i = y

        while i < y + h:

            draw.line(

                (

                    x + w,

                    i,

                    x + w,

                    min(i + dash, y + h)

                ),

                fill=colour,

                width=width

            )

            i += dash + gap

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

            # =====================================
            # Candidate Colour
            # =====================================

            colour = RED

            if candidate.get(

                "recovered",

                False

            ):

                colour = MAGENTA

            # =====================================
            # Draw Bounding Box
            # =====================================

          

        #
        # Normal detections
        #

        if not candidate.get(

            "recovered",

            False

        ):

            draw.rectangle(

                (

                    x,

                    y,

                    x + w,

                    y + h

                ),

                outline=colour,

                width=4

            )

        #
        # Recovered detections
        #

        else:

            self._draw_dashed_rectangle(

                draw,

                x,

                y,

                w,

                h,

                colour,

                dash=10,

                gap=6,

                width=4

            )

            # =====================================
            # Build Label
            # =====================================

            label = candidate.get(

                "id",

                "?"

            )

            family = candidate.get(

                "family",

                ""

            )

            if family:

                label += f" {family}"

            role = candidate.get(

                "role",

                ""

            )

            if role == "parent":

                label += " [P]"

            elif role == "variant":

                label += " [V]"

            elif role == "detail":

                label += " [D]"

            elif role == "lifestyle":

                label += " [L]"

            if candidate.get(

                "recovered",

                False

            ):

                label += " [REC]"

            # =====================================
            # Draw Label
            # =====================================

            draw.text(

                (

                    x,

                    max(

                        0,

                        y - 18

                    )

                ),

                label,

                fill=colour

            )


candidate_renderer = CandidateRenderer()