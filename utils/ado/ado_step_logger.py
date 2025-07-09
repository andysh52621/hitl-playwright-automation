# utils/ado/ado_step_logger.py
from datetime import datetime


class StepLogger:
    def __init__(self):
        self.steps = []

    def add_step(self, action: str, expected: str, outcome: str = "Passed"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.steps.append({
            "action": action,
            "expected": expected,
            "outcome": outcome,
            "timestamp": timestamp
        })

    def fail_step(self, action: str, expected: str, error_message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.steps.append({
            "action": action,
            "expected": expected,
            "outcome": f"Failed: {error_message}",
            "timestamp": timestamp
        })

    def get_steps(self):
        return self.steps

    def reset(self):
        self.steps = []
