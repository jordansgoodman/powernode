from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import shutil
import polars as pl

from src.workflow import Workflow
from src.node import ReadCSVNode, JoinNode

app = FastAPI()

workflows: Dict[str, Workflow] = {}

data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
app.mount("/files", StaticFiles(directory=data_path), name="files")


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
    return {"message": f"Workflow '{req.name}' created"}

@app.post("/workflow/{workflow_name}/read_node")
def add_read_node(workflow_name: str, req: AddReadNodeRequest):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    wf.add_node(ReadCSVNode, name=req.name, file_path=req.file_path)
    return {"message": f"ReadCSVNode '{req.name}' added"}

@app.post("/workflow/{workflow_name}/join_node")
def add_join_node(workflow_name: str, req: AddJoinNodeRequest):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    wf.add_node(JoinNode, name=req.name,
                left_table=req.left_table,
                right_table=req.right_table,
                on=req.on,
                how=req.how)
    return {"message": f"JoinNode '{req.name}' added"}

@app.post("/workflow/{workflow_name}/run")
def run_workflow(workflow_name: str):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    for node in wf.nodes:
        node.run()
    return {"message": "Workflow executed"}

@app.get("/workflow/{workflow_name}/nodes/{node_name}/preview")
def preview_node(workflow_name: str, node_name: str, limit: int = 5):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    node = next((n for n in wf.nodes if n.name == node_name), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    if hasattr(node.output, "fetch"):  # LazyFrame
        return node.output.fetch(limit).to_dicts()
    elif isinstance(node.output, str) and node.output.endswith(".parquet"):
        df = pl.read_parquet(node.output)
        return df.head(limit).to_dicts()
    else:
        raise HTTPException(status_code=400, detail="Node output not previewable")

# need to fix this: in memory vs disk
@app.delete("/workflow/{workflow_name}")
def delete_workflow(workflow_name: str):
    wf = workflows.pop(workflow_name, None)
    path = os.path.join("data", workflow_name)

    deleted_disk = False
    if os.path.exists(path):
        shutil.rmtree(path)
        deleted_disk = True

    if wf or deleted_disk:
        return {"status": "deleted", "workflow": workflow_name}
    
    raise HTTPException(status_code=404, detail="Workflow not found in memory or on disk")

@app.delete("/workflow/{workflow_name}/nodes/{node_name}/clear")
def clear_node_folder(workflow_name: str, node_name: str):
    folder = os.path.join("data", workflow_name, node_name)
    if not os.path.exists(folder):
        raise HTTPException(status_code=404, detail="Node folder not found")
    for file in os.listdir(folder):
        os.remove(os.path.join(folder, file))
    return {"status": "cleared", "folder": folder}
