from flask import request, jsonify
import logging
import base64
import io

from PIL import Image

from segmentation import recover_region

_logger = logging.getLogger(__name__)


#===========================================================
# Recover Page
#===========================================================

def recover_page():

    try:

        data = request.get_json(force=True)

        regions = data.get(

            "regions",

            []
        )

        _logger.warning(

            f"[RECOVERY START] "

            f"regions={len(regions)}"
        )

        assets = []

        for region in regions:

            recovered = recover_region(

                region
            )

            assets.extend(

                recovered
            )

        _logger.warning(

            f"[RECOVERY FINISH] "

            f"assets={len(assets)}"
        )

        return jsonify({

            "assets": assets
        })

    except Exception:

        _logger.exception(

            "[RECOVERY ERROR]"
        )

        return jsonify({

            "assets": []

        }), 500