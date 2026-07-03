import io

from flask import send_file

from .report_renderer import report_renderer


class PreviewGenerator:

    def preview(

        self,

        preview_data

    ):
        
        page_image = preview_data["page_image"]

        candidates = preview_data["candidates"]

        metadata = preview_data["metadata"]

        pipeline = preview_data["pipeline"]

        statistics = preview_data["statistics"]

        family = preview_data["family"]

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