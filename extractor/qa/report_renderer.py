from PIL import Image

from PIL import ImageDraw

from .candidate_renderer import candidate_renderer

from .metadata_renderer import metadata_renderer


class ReportRenderer:

    def build(

        self,

        page_image,

        candidates,

        metadata

    ):

        report = page_image.copy()

        draw = ImageDraw.Draw(

            report

        )

        candidate_renderer.render(

            draw,

            candidates

        )

        metadata_renderer.render(

            draw,

            metadata

        )

        return report


report_renderer = ReportRenderer()