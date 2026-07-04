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

        DEBUG_RETURN_IMAGES = False

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


            encoded = base64.b64encode(

                buffer.getvalue()

            ).decode("utf-8")

            #
            # Keep PIL image for QA Preview
            #

            product["crop_image"] = crop.copy()

            # Always keep production image

            product["image"] = encoded

            # Debug only

            product["image_size"] = len(encoded)

            product["crop_width"] = crop.width

            product["crop_height"] = crop.height

            output.append(product)

        _logger.warning(

            f"[PRODUCT CROPPER] "

            f"products={len(output)}"

        )

        return output


product_cropper = ProductCropper()