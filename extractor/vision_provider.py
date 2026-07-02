import logging

_logger = logging.getLogger(__name__)


class VisionProvider:

    def analyze(self, asset):

        """
        Placeholder implementation.

        Later this method will call an external
        semantic vision service.

        """

        result = {

            "label": "unknown",

            "confidence": 0.0,

            "provider": "placeholder",

            "reason": "No vision backend configured"

        }

        asset.metadata["vision"] = result

        return asset


vision_provider = VisionProvider()