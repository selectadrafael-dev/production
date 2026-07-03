import time


class ProcessingReport:

    def __init__(self):

        self.clear()

    # ==========================================
    # Reset report for every new PDF request
    # ==========================================
    def clear(self):

        self.steps = []

    # ==========================================
    # Add one pipeline step
    # ==========================================
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

    # ==========================================
    # Return report
    # ==========================================
    def to_dict(self):

        return self.steps


processing_report = ProcessingReport()