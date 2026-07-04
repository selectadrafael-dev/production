from PIL import ImageDraw

from .candidate_renderer import candidate_renderer
from .metadata_renderer import metadata_renderer


class ReportRenderer:

    def build(

        self,

        preview_data

    ):

        # ==========================================
        # Extract preview data
        # ==========================================

        page_image = preview_data["page_image"].copy()

        candidates = preview_data["candidates"]

        metadata = preview_data["metadata"]

        pipeline = preview_data["pipeline"]

        statistics = preview_data["statistics"]

        family = preview_data["family"]

        diagnostics = preview_data["diagnostics"]

        # ==========================================
        # Prepare canvas
        # ==========================================

        report = page_image

        draw = ImageDraw.Draw(

            report

        )

        # ==========================================
        # QA Header
        # ==========================================

        draw.text(

            (20, 20),

            f"CATALOG QA REPORT | FAMILY {family}",

            fill="black"

        )

        draw.text(

            (20, 45),

            f"Products: {statistics['candidates']} | "

            f"Metadata: {statistics['metadata_blocks']} | "

            f"Pipeline: {statistics['pipeline_steps']}",

            fill="black"

        )

        # ==========================================
        # Region Diagnostics
        # ==========================================

        for region in diagnostics:

            bbox = region["bbox"]

            x = bbox["x"]

            y = bbox["y"]

            w = bbox["width"]

            h = bbox["height"]

            color = "green" if region["selected"] else "orange"

            draw.rectangle(

                [

                    x,

                    y,

                    x + w,

                    y + h

                ],

                outline=color,

                width=3

            )

            draw.text(

                (

                    x,

                    max(

                        0,

                        y - 18

                    )

                ),

                f"{region['id']} | "

                f"{region['structure']} | "

                f"{region['products']}",

                fill=color

            )

        # ==========================================
        # Draw Product Candidates
        # ==========================================

        candidate_renderer.render(

            draw,

            candidates

        )

        # ==========================================
        # Draw Metadata Blocks
        # ==========================================

        metadata_renderer.render(

            draw,

            metadata

        )

        # ==========================================
        # Draw Pipeline Summary
        # ==========================================

        y = 80

        draw.text(

            (20, y),

            "PIPELINE",

            fill="blue"

        )

        y += 20

        for step in pipeline["steps"]:

            draw.text(

                (20, y),

                f"✓ {step['stage']}",

                fill="green"

            )

            y += 18

        return report


report_renderer = ReportRenderer()