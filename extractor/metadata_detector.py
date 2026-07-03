import re
import logging

_logger = logging.getLogger(__name__)


class MetadataDetector:

    PRICE = re.compile(

        r"\d+(?:[.,]\d+)?\s*(AZN|USD|EUR|\$|€|£)",

        re.I

    )

    STOCK = re.compile(

        r"\d+\s*(pcs?|pieces?)",

        re.I

    )


    SKU = re.compile(

        r"^[A-Z0-9]{2,8}[-_/][A-Z0-9]{2,12}$"

    )

    CAPACITY = re.compile(

        r"\d+(\.\d+)?\s*(ml|l|oz)",

        re.I

    )

    def detect(self, blocks):

        metadata = []

        for block in blocks:

            text = block["text"].strip()

            item = dict(block)

            item["type"] = "text"

            if self.PRICE.search(text):

                item["type"] = "price"

            elif self.STOCK.search(text):

                item["type"] = "stock"

            elif self.CAPACITY.search(text):

                item["type"] = "capacity"
            
            # ======================================
            # Long paragraph → Description
            # ======================================

            elif len(text.split()) > 12:

                item["type"] = "description"

            elif self.SKU.search(text):

                item["type"] = "sku"

            metadata.append(item)

        _logger.warning(

            f"[METADATA DETECTOR] "

            f"blocks={len(metadata)}"

        )

        return metadata


metadata_detector = MetadataDetector()