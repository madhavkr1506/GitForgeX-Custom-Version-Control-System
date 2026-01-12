import json
from pathlib import *
from Logging import *

class NodeReferenceState:
    def __init__(self):
        log = PrintLog()
        self.log = log.log

        self.working_module = Path("./.gitforgex")
        self.contents = {}

    def reading_node_state(self, filepath):
        try:
            contents = None
            with open(file=filepath, mode="r") as jsonfile:
                contents = json.load(jsonfile)
            jsonfile.close()

            self.contents = contents
        except Exception as e:
            self.log.error(f"reading node state failed: {str(e)}")

    def updating_node_state(self, filepath, payload):
        try:
            with open(file=filepath, mode="w") as jsonfile:
                json.dump(payload, jsonfile, indent=4)
            jsonfile.close()          
        except Exception as e:
            self.log.error(f"updating node state failed: {str(e)}")
            