from .low_contrast_recovery import low_contrast_recovery


class RecoveryEngine:

    def __init__(self):

        #
        # Recovery pipeline
        #
        # Every future recovery module
        # is added here.
        #

        self.pipeline = [

            low_contrast_recovery,

        ]

    def recover(

        self,

        page_image,

        assets,

        metadata,

        regions

    ):

        report = {

            "recovered": 0,

            "warnings": [],

            "modules": []

        }

        #
        # Execute every recovery module
        #

        for module in self.pipeline:

            assets, module_report = module.recover(

                page_image,

                assets,

                metadata,

                regions

            )

            report["recovered"] += module_report.get(

                "recovered",

                0

            )

            report["warnings"].extend(

                module_report.get(

                    "warnings",

                    []

                )

            )


            report["modules"].append({

                "module": module.__class__.__name__,

                "recovered": module_report.get("recovered", 0),

                "warnings": module_report.get("warnings", [])

            })

        return assets, report


recovery_engine = RecoveryEngine()