from PIL import Image


def analyze_page(image):

    return {

        "width": image.width,

        "height": image.height,

        "aspect_ratio":

            image.width /

            max(image.height, 1)

    }