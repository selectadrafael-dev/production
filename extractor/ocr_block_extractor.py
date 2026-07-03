import fitz

import logging

_logger = logging.getLogger(__name__)


class OCRBlockExtractor:

    def extract(

        self,

        page

    ):

        blocks = []

        raw = page.get_text("blocks")

        for block in raw:

            try:

                x0, y0, x1, y1, text, *_ = block

                text = text.strip()

                if not text:

                    continue

                blocks.append({

                    "text": text,

                    "bbox": {

                        "x": int(x0),

                        "y": int(y0),

                        "width": int(x1 - x0),

                        "height": int(y1 - y0)

                    }

                })

            except Exception:

                continue

        _logger.warning(

            f"[OCR BLOCKS] "

            f"{len(blocks)}"

        )

        return blocks


ocr_block_extractor = OCRBlockExtractor()