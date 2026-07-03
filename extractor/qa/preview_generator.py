import io

from flask import send_file

from .report_renderer import report_renderer


class PreviewGenerator:

    def preview(

        self,

        page_image,

        candidates,

        metadata

    ):

        report = report_renderer.build(

            page_image,

            candidates,

            metadata

        )

        buffer = io.BytesIO()

        report.save(

            buffer,

            format="PNG"

        )

        buffer.seek(0)

        return send_file(

            buffer,

            mimetype="image/png"

        )


preview_generator = PreviewGenerator()