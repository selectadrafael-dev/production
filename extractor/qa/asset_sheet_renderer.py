from PIL import Image

from PIL import ImageDraw


class AssetSheetRenderer:

    def build(

        self,

        preview_data

    ):

        page = preview_data["page_image"]

        candidates = preview_data["candidates"]

        #
        # Canvas
        #
        canvas = Image.new(

            "RGB",

            (

                page.width,

                page.height + 1200

            ),

            "white"

        )

        canvas.paste(

            page,

            (

                0,

                0

            )

        )

        draw = ImageDraw.Draw(canvas)

        draw.text(

            (

                20,

                page.height + 20

            ),

            "Detected Assets",

            fill="black"

        )

        #
        # Asset Grid
        #

        x = 20

        y = page.height + 60

        cell = 200

        for candidate in candidates:

            crop = candidate.get(

                "crop",

                {}

            ).get(

                "image"

            )

            #
            # Skip empty crops
            #

            if crop is None:

                continue

            thumb = crop.copy()

            thumb.thumbnail(

                (

                    170,

                    170

                )

            )

            canvas.paste(

                thumb,

                (

                    x,

                    y

                )

            )

            draw.text(

                (

                    x,

                    y + 175

                ),

                candidate["id"],

                fill="black"

            )

            x += cell

            if x + cell > page.width:

                x = 20

                y += 220

        return canvas

asset_sheet_renderer = AssetSheetRenderer()