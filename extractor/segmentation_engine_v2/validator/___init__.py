import logging
from .size_validator import size_validator
from .aspect_validator import aspect_validator
from .white_object_validator import white_object_validator
from .duplicate_validator import duplicate_validator
from .confidence_validator import confidence_validator

_logger = logging.getLogger(__name__)


class ValidatorEngine:

    def validate(

        self,

        page_image,

        regions

    ):

        output = []

        for region in regions:

            #
            # Size Validation
            #

            if not size_validator.validate(
                region
            ):
                continue

            #
            # Aspect Ratio Validation
            #

            if not aspect_validator.validate(
                region
            ):
                continue

            #
            # White Object Validation
            #

            if not white_object_validator.validate(

                page_image,

                region

            ):
                continue


            if not duplicate_validator.validate(

                region,

                output

            ):
                continue

            if not confidence_validator.validate(

                region

            ):
                continue

            output.append(
                region
            )

        _logger.warning(

            "[VALIDATOR] "

            f"Accepted={len(output)}"

        )
        
        return output


validator = ValidatorEngine()
