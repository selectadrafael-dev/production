import logging
from PIL import ImageDraw

_logger = logging.getLogger(__name__)


class PreviewGenerator:

    def draw(

        self,

        image,

        candidates

    ):

        preview = image.copy()

        draw = ImageDraw.Draw(preview)

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

                    x + w,

                    y + h

                ),

                outline="red",

                width=4

            )

            draw.text(

                (

                    x,

                    max(

                        0,

                        y - 20

                    )

                ),

                candidate["id"],

                fill="red"

            )

            meta = candidate.get(

                "metadata",

                {}

            )

            lines = []

            if meta.get("stock"):

                lines.append(

                    f"Stock: {meta['stock']}"

                )

            if meta.get("price"):

                lines.append(

                    f"Price: {meta['price']}"

                )

            if meta.get("sku"):

                lines.append(

                    f"SKU: {meta['sku']}"

                )

            for index, line in enumerate(lines):

                draw.text(

                    (

                        x,

                        y + h + 5 + (index * 18)

                    ),

                    line,

                    fill="blue"

                )

        return preview


preview_generator = PreviewGenerator()