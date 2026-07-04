from PIL import Image

from PIL import ImageDraw


class AssetSheetRenderer:

    def build(

        self,

        preview_data

    ):

        page = preview_data["page_image"]

        candidates = preview_data["candidates"]

        return page


asset_sheet_renderer = AssetSheetRenderer()