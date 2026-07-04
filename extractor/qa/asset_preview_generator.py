import io

from flask import send_file

from .asset_sheet_renderer import asset_sheet_renderer


class AssetPreviewGenerator:

    def preview(

        self,

        preview_data

    ):

        report = asset_sheet_renderer.build(

            preview_data

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


asset_preview_generator = AssetPreviewGenerator()