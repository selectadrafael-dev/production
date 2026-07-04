import math


class ProductRelationshipEngine:

    # ==========================================
    # Euclidean distance
    # ==========================================

    def _distance(

        self,

        a,

        b

    ):

        ax = a["bbox"]["x"] + a["bbox"]["width"] / 2
        ay = a["bbox"]["y"] + a["bbox"]["height"] / 2

        bx = b["bbox"]["x"] + b["bbox"]["width"] / 2
        by = b["bbox"]["y"] + b["bbox"]["height"] / 2

        return math.sqrt(

            (ax - bx) ** 2 +

            (ay - by) ** 2

        )

    # ==========================================
    # Build Product Families
    # ==========================================

    def build(

        self,

        candidates,

        metadata

    ):

        if not candidates:

            return candidates

        #
        # Sort by size (largest first)
        #

        ordered = sorted(

            candidates,

            key=lambda c:

            c["bbox"]["width"] *

            c["bbox"]["height"],

            reverse=True

        )

        family_counter = 1

        visited = set()

        for parent in ordered:

            if parent["id"] in visited:

                continue

            family_id = f"F{family_counter}"

            family_counter += 1

            parent["role"] = "parent"

            parent["family"] = family_id

            parent["variants"] = []

            visited.add(

                parent["id"]

            )

            #
            # Find nearby candidates
            #

            for child in ordered:

                if child["id"] in visited:

                    continue

                distance = self._distance(

                    parent,

                    child

                )

                #
                # Initial threshold.
                # We'll tune later.
                #

                if distance < 450:

                    child["role"] = "variant"

                    child["parent"] = parent["id"]

                    child["family"] = family_id

                    parent["variants"].append(

                        child["id"]

                    )

                    visited.add(

                        child["id"]

                    )

        return ordered


product_relationship_engine = ProductRelationshipEngine()