import logging
import cv2
import numpy as np

_logger = logging.getLogger(__name__)


class ProductGridSplitter:

    def split(

        self,

        page_image,

        products

    ):

        output = []

        for product in products:

            # Skip non-grid regions
            if product.get("structure") != "product_grid":

                output.append(product)

                continue

            x = product["x"]
            y = product["y"]
            w = product["width"]
            h = product["height"]

            roi = page_image.crop(

                (

                    x,

                    y,

                    x + w,

                    y + h

                )

            )

            img = np.array(roi)

            gray = cv2.cvtColor(

                img,

                cv2.COLOR_RGB2GRAY

            )

            projection = np.mean(

                gray,

                axis=0

            )

            threshold = np.mean(projection)

            gaps = []

            start = None

            for i, value in enumerate(projection):

                if value > threshold:

                    if start is None:

                        start = i

                else:

                    if start is not None:

                        gaps.append((start, i))

                        start = None

            _logger.warning(

                f"[GRID SPLITTER] "

                f"columns={len(gaps)}"

            )

            output.append(product)

        return output


product_grid_splitter = ProductGridSplitter()