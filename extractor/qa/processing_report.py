import time


class ProcessingReport:

    def __init__(self):

        self.clear()

    def clear(self):

        self.started = time.time()

        self.steps = []

    def add(

        self,

        stage,

        status,

        details=None

    ):

        self.steps.append({

            "elapsed": round(

                time.time() - self.started,

                3

            ),

            "stage": stage,

            "status": status,

            "details": details or {}

        })

    def summary(self):

        return {

            "steps": len(self.steps),

            "duration": round(

                time.time() - self.started,

                3

            )

        }

    def to_dict(self):

        return {

            "summary": self.summary(),

            "steps": self.steps

        }
    


processing_report = ProcessingReport()