from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from PIL import Image
import base64
import io
import numpy as np

app = FastAPI()

model = SentenceTransformer(
    'clip-ViT-B-32'
)

class MatchRequest(BaseModel):

    variant_text: str

    images: list


@app.post("/match")

def match_variant(request: MatchRequest):

    try:

        text_embedding = model.encode(
            request.variant_text
        )

        best_index = None

        best_score = -999

        for idx, image_b64 in enumerate(request.images):

            try:

                image_data = base64.b64decode(
                    image_b64
                )

                pil_image = Image.open(
                    io.BytesIO(image_data)
                ).convert("RGB")

                image_embedding = model.encode(
                    pil_image
                )

                similarity = np.dot(
                    text_embedding,
                    image_embedding
                ) / (
                    np.linalg.norm(text_embedding)
                    * np.linalg.norm(image_embedding)
                )

                if similarity > best_score:

                    best_score = similarity

                    best_index = idx

            except Exception:
                continue

        return {
            "best_index": best_index,
            "score": float(best_score)
        }

    except Exception as e:

        return {
            "error": str(e)
        }