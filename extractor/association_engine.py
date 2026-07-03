import logging

_logger = logging.getLogger(__name__)


class AssociationEngine:

    def associate(

        self,

        candidates,

        metadata

    ):

        for candidate in candidates:

            bbox = candidate["bbox"]

            left = bbox["x"]
            right = bbox["x"] + bbox["width"]

            bottom = bbox["y"] + bbox["height"]

            candidate["metadata"] = {}

            for block in metadata:

                bx = block["bbox"]["x"]

                by = block["bbox"]["y"]

                # Metadata must be below product

                if by < bottom:

                    continue

                # Horizontal alignment

                if bx < left - 150:

                    continue

                if bx > right + 150:

                    continue

                candidate["metadata"][

                    block["type"]

                ] = block["text"]

            _logger.warning(

                f"[ASSOCIATION] "

                f"{candidate['id']} "

                f"{candidate['metadata']}"

            )

        return candidates


association_engine = AssociationEngine()