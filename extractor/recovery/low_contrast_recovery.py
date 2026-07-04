import cv2
import numpy as np


class LowContrastRecovery:

    def recover(

        self,

        page_image,

        assets,

        metadata,

        regions

    ):

        recovered = 0

        warnings = []

        img = np.array(page_image)

        for region in regions:

            #
            # Only inspect product regions
            #

            if region.get("label") != "product":

                continue

            x = region["x"]
            y = region["y"]
            w = region["width"]
            h = region["height"]

            roi = img[y:y+h, x:x+w]

            if roi.size == 0:

                continue

            gray = cv2.cvtColor(

                roi,

                cv2.COLOR_RGB2GRAY

            )

            #
            # Contrast
            #

            contrast = gray.std()

            #
            # Ignore normal regions
            #

            if contrast > 25:

                continue

            #
            # Adaptive Threshold
            #

            binary = cv2.adaptiveThreshold(

                gray,

                255,

                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

                cv2.THRESH_BINARY_INV,

                31,

                3

            )

            contours, _ = cv2.findContours(

                binary,

                cv2.RETR_EXTERNAL,

                cv2.CHAIN_APPROX_SIMPLE

            )

            for contour in contours:

                rx, ry, rw, rh = cv2.boundingRect(

                    contour

                )

                area = rw * rh

                if area < 6000:

                    continue

                #
                # Prevent duplicates
                #

                duplicate = False

                for asset in assets:

                    b = asset["bbox"]

                    if (

                        abs(b["x"]-(x+rx)) < 20

                        and

                        abs(b["y"]-(y+ry)) < 20

                    ):

                        duplicate = True

                        break

                if duplicate:

                    continue

                assets.append({

                    "id": f"REC{recovered+1}",

                    "bbox": {

                        "x": x+rx,

                        "y": y+ry,

                        "width": rw,

                        "height": rh

                    },

                    "classification": "product",

                    "role": "recovered",

                    "recovered": True

                })

                recovered += 1

        return assets, {

            "recovered": recovered,

            "warnings": warnings

        }


low_contrast_recovery = LowContrastRecovery()