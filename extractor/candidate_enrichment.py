import logging

_logger = logging.getLogger(__name__)


class CandidateEnrichment:

    def enrich(

        self,

        candidates,

        metadata_blocks

    ):

        for candidate in candidates:

            candidate["metadata_matches"] = []

            bbox = candidate["bbox"]

            bottom = (

                bbox["y"]

                +

                bbox["height"]

            )

            left = bbox["x"]

            right = (

                bbox["x"]

                +

                bbox["width"]

            )

            for block in metadata_blocks:

                by = block["bbox"]["y"]

                bx = block["bbox"]["x"]

                if (

                    by >= bottom

                    and

                    abs(

                        bx -

                        left

                    ) < 250

                ):

                    candidate[

                        "metadata_matches"

                    ].append(

                        block

                    )

            _logger.warning(

                f"[ENRICHMENT] "

                f"{candidate['id']} "

                f"metadata={len(candidate['metadata_matches'])}"

            )

        return candidates


candidate_enrichment = CandidateEnrichment()