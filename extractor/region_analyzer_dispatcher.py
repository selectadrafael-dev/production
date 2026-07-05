from hero_region_analyzer import hero_region_analyzer
from variant_region_analyzer import variant_region_analyzer
from gallery_region_analyzer import gallery_region_analyzer
from product_region_analyzer_v2 import (

    product_region_analyzer_v2

)


class RegionAnalyzerDispatcher:

    def analyze(

        self,

        image,

        regions

    ):

        output = []

        for region in regions:

            region_type = region.get(

                "type"

            )

            if region_type == "hero":

                output.extend(

                    hero_region_analyzer.analyze(

                        image,

                        region

                    )

                )

            elif region_type == "product":

                output.extend(

                    product_region_analyzer_v2.analyze(

                        image,

                        region

                    )

                )

            else:

                output.extend(

                    gallery_region_analyzer.analyze(

                        image,

                        region

                    )

                )

        return output


region_analyzer_dispatcher = RegionAnalyzerDispatcher()