import logging

_logger = logging.getLogger(__name__)


class DecisionEngine:

    PRODUCT_THRESHOLD = 70

    def process(self, page):

        accepted = 0
        rejected = 0

        for asset in page.assets:

            score = 0
            reasons = []

            image = asset.image or {}
            vision = asset.metadata.get("vision", {})

            # ----------------------------------
            # Existing metadata
            # ----------------------------------

            if image.get("hero_score", 0) >= 0.50:
                score += 20
                reasons.append("hero")

            if image.get("gallery_score", 0) >= 0.50:
                score += 15
                reasons.append("gallery")

            if not image.get("is_lifestyle"):
                score += 20
                reasons.append("not_lifestyle")

            # ----------------------------------
            # Vision result
            # ----------------------------------

            if vision.get("label") == "product":
                score += 45
                reasons.append("vision_product")

            if vision.get("confidence", 0) >= 0.90:
                score += 20
                reasons.append("vision_confident")

            asset.metadata["decision"] = {

                "score": score,

                "reasons": reasons

            }

            if score >= self.PRODUCT_THRESHOLD:

                asset.certified = True
                asset.rejected = False

                accepted += 1

            else:

                asset.certified = False
                asset.rejected = True
                asset.rejection_reason = "decision_score"

                rejected += 1

        _logger.warning(

            "[DECISION ENGINE] "

            f"accepted={accepted} "

            f"rejected={rejected}"

        )

        return page


decision_engine = DecisionEngine()