import io
import base64
import logging

from PIL import Image

_logger = logging.getLogger(__name__)


class ProductCropper:

    def crop(

        self,

        page_image,

        products

    ):

        output = []

        for product in products:

            if product["structure"] == "hero_banner":

                _logger.warning(

                    "[CROPPER] "

                    "Skipping Hero Banner"

                )

                continue

            if product["structure"] == "lifestyle":
                _logger.warning(

                    "[CROPPER] "

                    "Skipping Lifestyle Banner"

                )

                continue

            x = product["x"]
            y = product["y"]
            w = product["width"]
            h = product["height"]

            crop = page_image.crop(

                (

                    x,

                    y,

                    x + w,

                    y + h

                )

            )

            buffer = io.BytesIO()

            crop.save(

                buffer,

                format="JPEG",

                quality=90

            )

            product["image"] = base64.b64encode(

                buffer.getvalue()

            ).decode("utf-8")

            output.append(product)

        _logger.warning(

            f"[PRODUCT CROPPER] "

            f"products={len(output)}"

        )

        return output


product_cropper = ProductCropper()