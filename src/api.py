from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import polars as pl
import os

from src.workflow import Workflow
from src.node import ReadCSVNode, JoinNode

app = FastAPI()

workflows: Dict[str, Workflow] = {}


class CreateWorkflowRequest(BaseModel):
    name: str

class AddReadNodeRequest(BaseModel):
    name: str
    file_path: str

class AddJoinNodeRequest(BaseModel):
    name: str
    left_table: str
    right_table: str
    on: List[str]
    how: Optional[str] = "inner"

@app.post("/workflow")
def create_workflow(req: CreateWorkflowRequest):
    if req.name in workflows:
        raise HTTPException(status_code=400, detail="Workflow already exists")

    wf = Workflow(name=req.name)
    workflows[req.name] = wf
    return {"message": f"Workflow '{req.name}' created successfully"}

@app.post("/workflow/{workflow_name}/read_node")
def add_read_node(workflow_name: str, req: AddReadNodeRequest):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    node = wf.add_node(
        ReadCSVNode,
        name=req.name,
        file_path=req.file_path
    )
    return {"message": f"ReadCSVNode '{req.name}' added."}

@app.post("/workflow/{workflow_name}/join_node")
def add_join_node(workflow_name: str, req: AddJoinNodeRequest):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    node = wf.add_node(
        JoinNode,
        name=req.name,
        left_table=req.left_table,
        right_table=req.right_table,
        on=req.on,
        how=req.how
    )
    return {"message": f"JoinNode '{req.name}' added."}

@app.post("/workflow/{workflow_name}/run")
def run_workflow(workflow_name: str):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    for node in wf.nodes:
        node.run()

    return {"message": f"Workflow '{workflow_name}' executed."}

@app.get("/workflow/{workflow_name}/nodes/{node_name}/preview")
def preview_node(workflow_name: str, node_name: str, limit: int = 5):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    node = next((n for n in wf.nodes if n.name == node_name), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    if hasattr(node.output, "fetch"):  # join node with LazyFrame
        return node.output.fetch(limit).to_dicts()
    elif isinstance(node.output, str) and node.output.endswith(".parquet"):  # read node
        df = pl.read_parquet(node.output)
        return df.head(limit).to_dicts()
    else:
        raise HTTPException(status_code=400, detail="Node output not previewable")

@app.get("/workflow")
def list_workflows():
    return {"workflows": list(workflows.keys())}
