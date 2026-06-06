from fastapi import FastAPI

from pydantic import BaseModel

from transformers import (
    CLIPProcessor,
    CLIPModel
)

from PIL import Image

import torch
import numpy as np

import base64
import io

# =====================================
# CPU OPTIMIZATION
# =====================================

torch.set_num_threads(1)

# =====================================
# LOAD CLIP
# =====================================

model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)

processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)

# =====================================
# FASTAPI
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
# MATCH ENDPOINT
# =====================================

@app.post("/match")

def match_variant(request: MatchRequest):

    try:

        if not request.images:

            return {
                "best_index": None,
                "score": 0
            }

        best_score = -999.0

        best_index = None

        # =====================================
        # PROCESS TEXT ONCE
        # =====================================

        text_inputs = processor(

            text=[request.variant_text],

            return_tensors="pt",

            padding=True
        )

        with torch.no_grad():

            text_features = model.get_text_features(
                **text_inputs
            )

        text_features = text_features[0]

        # =====================================
        # LOOP IMAGES
        # =====================================

        for idx, image_b64 in enumerate(
            request.images
        ):

            try:

                image_data = base64.b64decode(
                    image_b64
                )

                pil_image = Image.open(

                    io.BytesIO(image_data)

                ).convert("RGB")

                # =====================================
                # REDUCE IMAGE SIZE
                # =====================================

                pil_image.thumbnail((512, 512))

                image_inputs = processor(

                    images=pil_image,

                    return_tensors="pt"
                )

                with torch.no_grad():

                    image_features = (

                        model.get_image_features(
                            **image_inputs
                        )
                    )

                image_features = image_features[0]

                similarity = torch.cosine_similarity(

                    text_features.unsqueeze(0),

                    image_features.unsqueeze(0)

                ).item()

                if similarity > best_score:

                    best_score = similarity

                    best_index = idx

            except Exception as image_error:

                print(
                    f"[IMAGE ERROR] {str(image_error)}"
                )

                continue

        return {

            "best_index": best_index,

            "score": float(best_score)
        }

    except Exception as e:

        return {
            "error": str(e)
        }
