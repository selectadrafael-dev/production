"""
serializer.py
Family B Response Adapter - Serialization helpers.
"""
import base64, io
try:
    from PIL import Image
except Exception:
    Image = None

class ResponseSerializer:
    def serialize_image(self, value):
        if Image is not None and isinstance(value, Image.Image):
            buf = io.BytesIO()
            value.convert("RGB").save(buf, format="JPEG", quality=85)
            return base64.b64encode(buf.getvalue()).decode("utf-8")
        return value

    def sanitize(self, value):
        if Image is not None and isinstance(value, Image.Image):
            return self.serialize_image(value)
        if isinstance(value, dict):
            out = {}
            for k, v in value.items():
                if k == "crop" and isinstance(v, dict):
                    img = v.get("image")
                    if img is not None:
                        out["image"] = self.serialize_image(img)
                    for ck, cv in v.items():
                        if ck != "image":
                            out[ck] = self.sanitize(cv)
                else:
                    out[k] = self.sanitize(v)
            return out
        if isinstance(value, (list, tuple)):
            return [self.sanitize(v) for v in value]
        try:
            import numpy as np
            if isinstance(value, np.ndarray):
                return value.tolist()
        except Exception:
            pass
        return value

response_serializer = ResponseSerializer()
