import logging

_logger = logging.getLogger(__name__)


class LayoutProfiler:

    def build(self, image, regions):

        large = 0
        medium = 0
        small = 0

        page_width = image.width
        page_height = image.height

        for region in regions:

            area_ratio = region["area"] / (
                page_width * page_height
            )

            if area_ratio > 0.12:

                large += 1

            elif area_ratio > 0.03:

                medium += 1

            else:

                small += 1

        profile = {

            "large_regions": large,

            "medium_regions": medium,

            "small_regions": small,

            "total_regions": len(regions)

        }

        _logger.warning(

            f"[LAYOUT PROFILE] {profile}"

        )

        return profile


layout_profiler = LayoutProfiler()