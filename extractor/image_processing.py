from image_processing import (

    encode_image,

    numpy_to_pil
)
import logging
import base64

import cv2
import numpy as np

from PIL import Image

_logger = logging.getLogger(__name__)

#==========encode image==========================
def encode_image(

    pil_image,

    quality=75
):

    try:

        buffer = io.BytesIO()

        pil_image.save(

            buffer,

            format="JPEG",

            quality=quality
        )

        # return base64.b64encode(

        #     buffer.getvalue()

        # ).decode("utf-8")

    except Exception:

        _logger.exception(

            "[IMAGE ENCODE ERROR]"

        )

        return ""

#==========decode image==========================
def decode_image(

    image_base64

):
    try:

        image = Image.open(

            # io.BytesIO(

            #     base64.b64decode(

            #         image_base64
            #     )
            # )
        )

        return image

    except Exception:

        _logger.exception(

            "[IMAGE DECODE ERROR]"

        )

        return None
    

#==========pil to numpy==========================
def pil_to_numpy(

    pil_image

):
    
    return np.array(

        pil_image
    )


#==========numpy to pil==========================
def numpy_to_pil(

    image

):
    
    return Image.fromarray(

        image
    )


#==========safe crop==========================
def safe_crop(

    image,

    x,

    y,

    w,

    h
):
    
    height, width = image.shape[:2]

    x = max(

        0,

        x
    )

    y = max(

        0,

        y
    )

    w = min(

        w,

        width - x
    )

    h = min(

        h,

        height - y
    )

    return image[

        y:y+h,

        x:x+w

    ]

#==========thumbnail==========================
def create_thumbnail(

    pil_image,

    size=(300,300)
):
    
    thumb = pil_image.copy()

    thumb.thumbnail(

        size
    )

    return thumb