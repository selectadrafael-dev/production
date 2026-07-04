import logging

_logger = logging.getLogger(__name__)


class PipelineTracer:

    def stage(

        self,

        stage,

        items=None

    ):

        count = 0

        if items is not None:

            try:

                count = len(items)

            except Exception:

                count = 1

        _logger.warning(

            f"[PIPELINE] "

            f"{stage} "

            f"count={count}"

        )

        return items

    def region(

        self,

        stage,

        region

    ):

        _logger.warning(

            "[REGION] "

            f"{stage} "

            f"x={region.get('x')} "

            f"y={region.get('y')} "

            f"w={region.get('width')} "

            f"h={region.get('height')}"

        )


pipeline_tracer = PipelineTracer()