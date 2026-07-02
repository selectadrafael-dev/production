import logging

_logger = logging.getLogger(__name__)


class QualityGate:

    MIN_WIDTH = 120
    MIN_HEIGHT = 120
    MIN_HERO_SCORE = 0.10

    def process(self, page):

        accepted = 0
        rejected = 0

        for asset in page.assets:

            image = asset.image or {}

            reasons = []

            width = image.get("width", 0)
            height = image.get("height", 0)

            if width < self.MIN_WIDTH:

                reasons.append("width_too_small")

            if height < self.MIN_HEIGHT:

                reasons.append("height_too_small")

            if image.get("is_lifestyle"):

                reasons.append("lifestyle")

            if image.get("hero_score", 0) < self.MIN_HERO_SCORE:

                reasons.append("low_hero_score")

            if reasons:

                asset.rejected = True
                asset.rejection_reason = ",".join(reasons)

                rejected += 1

            else:

                asset.certified = True

                accepted += 1

        _logger.warning(

            "[QUALITY GATE] "

            f"accepted={accepted} "

            f"rejected={rejected}"

        )

        return page


quality_gate = QualityGate()