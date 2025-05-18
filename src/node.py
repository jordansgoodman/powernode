import uuid
import os
import datetime
import polars as pl

class Node:
    
    def __init__(self, name, workflow_path):

        self.id = str(uuid.uuid4())
        self.name = name
        self.created_at = datetime.datetime.now()
        self.status = "idle"
        self.inputs = []
        self.output = None
        self.func = None

        # Create this node's folder within the workflow directory
        self.path = os.path.join(workflow_path, self.name)
        os.makedirs(self.path, exist_ok=True)
    
    def run(self):
        raise NotImplementedError("run() must be implemented in subclasses")


class ReadCSVNode(Node):

    def __init__(self,name,workflow_path,file_path):
        super().__init__(name,workflow_path)
        self.file_path = file_path 

    def run(self):
        self.status = "running"
        try:
            self.output = pl.read_csv(self.file_path, infer_schema_length=100, low_memory=True).lazy()
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            raise e