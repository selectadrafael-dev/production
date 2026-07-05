"""
builder.py
Family B Response Adapter - builds Family A compatible response.
"""
from .serializer import response_serializer

class FamilyBResponseBuilder:

    def build(self, response_data, preview=False):
        response_data = response_serializer.sanitize(response_data)

        pages = []

        candidates = response_data.get("candidates", [])
        text = response_data.get("text", "")

        images = []

        for item in candidates:
            if not isinstance(item, dict):
                continue

            if "image" in item:
                images.append({
                    "image": item.get("image"),
                    "width": item.get("width", 0),
                    "height": item.get("height", 0),
                    "x": item.get("x", 0),
                    "y": item.get("y", 0),
                    "score": item.get("score", 0),
                    "is_lifestyle": item.get("is_lifestyle", False),
                })

        pages.append({
            "page": 1,
            "text": text,
            "images": images,
        })

        result = {"pages": pages}

        if preview:
            debug = {}
            for key in ("pipeline","statistics","diagnostics","regions","selected_regions","family"):
                if key in response_data:
                    debug[key]=response_data[key]
            result["debug"]=debug

        return result

family_b_response_builder = FamilyBResponseBuilder()
