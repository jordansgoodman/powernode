import uuid 
import os 
import datetime
from src.node import Node
import shutil

class Workflow:

    def __init__(self, name):

        # metadata
        self.name = name
        self.id = str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.last_run_at = None
        self.status = "idle"

        # define workflow directory based on user-provided name
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(script_dir, ".."))
        self.path = os.path.join(root_dir, "data", self.name)

        # # create the directory if it doesn't exist
        # if not os.path.exists(self.path):
        #     os.makedirs(self.path)
        
        # if os.path.exists(self.path):
        #     shutil.rmtree(self.path)
        # os.makedirs(self.path)

        # state
        self.graph = {}
        self.nodes = []
    
    def __str__(self):
        return (
            f"Workflow '{self.name}'\n"
            f"  ID: {self.id}\n"
            f"  Created: {self.created_at}\n"
            f"  Status: {self.status}\n"
            f"  Path: {self.path}\n"
            f"  Nodes: {len(self.nodes)}"
        )

    def add_node(self, node_cls, name=None, **kwargs):
        index = len(self.nodes) + 1
        node_name = name or f"node{index}"
        node = node_cls(node_name, self.path, **kwargs)
        self.nodes.append(node)
        return node
    
    def clear_all_nodes(self):
        for node in self.nodes:
            node.delete()
        self.nodes = []
