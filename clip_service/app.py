from fastapi import FastAPI
from pydantic import BaseModel

from sentence_transformers import SentenceTransformer

from PIL import Image

import base64
import io
import numpy as np
import torch

# =====================================
# CPU/RAM OPTIMIZATION
# =====================================

torch.set_num_threads(1)

# =====================================
# LOAD MODEL ONLY ONCE
# =====================================

model = SentenceTransformer(
    "clip-ViT-B-32"
)

# =====================================
# FASTAPI APP
# =====================================

app = FastAPI()

# =====================================
# REQUEST SCHEMA
# =====================================

class MatchRequest(BaseModel):

    variant_text: str

    images: list[str]

# =====================================
# HEALTH CHECK
# =====================================

@app.get("/")

def home():

    return {
        "status": "running"
    }

# =====================================
# CLIP MATCH ENDPOINT
# =====================================

@app.post("/match")

def match_variant(request: MatchRequest):

    try:

        # =====================================
        # SAFETY CHECK
        # =====================================

        if not request.images:

            return {
                "best_index": None,
                "score": 0
            }

        # =====================================
        # LIMIT IMAGE COUNT
        # IMPORTANT FOR RAM
        # =====================================

        images = request.images[:12]

        # =====================================
        # TEXT EMBEDDING
        # =====================================

        text_embedding = model.encode(
            request.variant_text,
            convert_to_numpy=True
        )

        best_index = None

        best_score = -999.0

        # =====================================
        # PROCESS IMAGES
        # =====================================

        for idx, image_b64 in enumerate(images):

            try:

                image_data = base64.b64decode(
                    image_b64
                )

                pil_image = Image.open(

                    io.BytesIO(image_data)

                ).convert("RGB")

                # =====================================
                # REDUCE MEMORY PRESSURE
                # =====================================

                pil_image.thumbnail((512, 512))

                # =====================================
                # IMAGE EMBEDDING
                # =====================================

                image_embedding = model.encode(
                    pil_image,
                    convert_to_numpy=True
                )

                # =====================================
                # COSINE SIMILARITY
                # =====================================

                similarity = np.dot(
                    text_embedding,
                    image_embedding
                ) / (
                    np.linalg.norm(text_embedding)
                    *
                    np.linalg.norm(image_embedding)
                )

                similarity = float(similarity)

                # =====================================
                # BEST MATCH
                # =====================================

                if similarity > best_score:

                    best_score = similarity

                    best_index = idx

            except Exception as image_error:

                print(
                    f"[IMAGE ERROR] "
                    f"{str(image_error)}"
                )

                continue

        # =====================================
        # RESPONSE
        # =====================================

        return {

            "best_index": best_index,

            "score": float(best_score)
        }

    except Exception as e:

        return {

            "error": str(e)
        }
