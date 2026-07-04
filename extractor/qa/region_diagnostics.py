class RegionDiagnostics:

    def build(

        self,

        classified_regions,

        selected_regions

    ):

        diagnostics = []

        selected_lookup = {

            id(region)

            for region in selected_regions

        }

        for index, region in enumerate(

            classified_regions,

            start=1

        ):


            diagnostics.append({

                "id": f"R{index}",

                "type": region.get(

                    "type"

                ),

                "label": region.get(

                    "label"

                ),

                "structure": region.get(

                    "structure",

                    "unknown"

                ),

                "selected": id(region) in selected_lookup,

                "products": region.get(

                    "detected_products",

                    0

                ),

                "bbox": {

                    "x": region["x"],

                    "y": region["y"],

                    "width": region["width"],

                    "height": region["height"]

                }

            })

        return diagnostics


region_diagnostics = RegionDiagnostics()