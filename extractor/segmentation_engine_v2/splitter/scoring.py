"""
segmentation_engine_v2/splitter/scoring.py

Deliverable #9
Assigns a quality score to split regions so later stages can
prefer higher-confidence detections.
"""

import logging

_logger = logging.getLogger(__name__)


class SplitScoring:

    def score(self, regions):

        scored = []

        for region in regions:

            width = region.get("width", 0)
            height = region.get("height", 0)
            area = width * height

            aspect = max(width, height) / max(1, min(width, height))

            score = 100.0

            if area < 1200:
                score -= 40

            if aspect > 3.0:
                score -= 25

            if aspect > 5.0:
                score -= 20

            region["score"] = max(score, 0)

            scored.append(region)

        scored.sort(
            key=lambda r: r.get("score", 0),
            reverse=True
        )

        _logger.warning(
            "[SCORING] regions=%d best=%.1f",
            len(scored),
            scored[0]["score"] if scored else 0
        )

        return scored


split_scoring = SplitScoring()
