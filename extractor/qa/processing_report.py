import time


class ProcessingReport:

    def __init__(self):

        self.steps = []

    def add(

        self,

        stage,

        status,

        details=None

    ):

        self.steps.append({

            "time": round(

                time.time(),

                3

            ),

            "stage": stage,

            "status": status,

            "details": details or {}

        })

    def to_dict(self):

        return self.steps


processing_report = ProcessingReport()