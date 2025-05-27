from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import shutil
import polars as pl
from src.workflow import Workflow
from src.node import ReadCSVNode, JoinNode, FilterNode
from fastapi.middleware.cors import CORSMiddleware
import datetime 
from src.log import init_action_log, register_action


app = FastAPI()

workflows: Dict[str, Workflow] = {}

data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
app.mount("/files", StaticFiles(directory=data_path), name="files")

init_action_log()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

class AddFilterNodeRequest(BaseModel):
    name: str
    input_table: str
    filter_expr: str   # e.g. "pl.col('Revenue') > 1000"

@app.get("/workflows")
def list_workflows():
    return [
        {
            "name": wf.name,
            "status": wf.status,
            "last_run_at": str(wf.last_run_at) if wf.last_run_at else None,
            "completed_at": str(wf.completed_at) if wf.completed_at else None,
            "failed_nodes": wf.failed_nodes,
        }
        for wf in workflows.values()
    ]
@app.get("/workflow/{workflow_name}/nodes")
def list_nodes(workflow_name: str):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return [{"name": n.name, "status": n.status, "type": n.__class__.__name__} for n in wf.nodes]

@app.post("/workflow/{workflow_name}/nodes/{node_name}/run")
def run_node(workflow_name: str, node_name: str):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    node = next((n for n in wf.nodes if n.name == node_name), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.run()
    return {"status": "completed", "node": node.name}


@app.delete("/workflow/{workflow_name}/nodes/{node_name}")
def delete_node(workflow_name: str, node_name: str):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    node = next((n for n in wf.nodes if n.name == node_name), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Delete folder
    node.delete()
    # Remove from list
    wf.nodes = [n for n in wf.nodes if n.name != node_name]
    return {"status": "deleted", "node": node_name}


@app.post("/workflow")
def create_workflow(req: CreateWorkflowRequest):
    if req.name in workflows:
        raise HTTPException(status_code=400, detail="Workflow already exists")

    wf = Workflow(name=req.name)
    workflows[req.name] = wf

    register_action(
        action="create_workflow",
        workflow=wf.name,
        payload=req.dict()
    )

    return {"message": f"Workflow '{req.name}' created"}

@app.post("/workflow/{workflow_name}/read_node")
def add_read_node(workflow_name: str, req: AddReadNodeRequest):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    wf.add_node(ReadCSVNode, name=req.name, file_path=req.file_path)

    register_action(
        action="add_read_node",
        workflow=workflow_name,
        payload=req.dict()
    )
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
    
    register_action(
        action="add_join_node",
        workflow=wf.name,
        payload=req.dict()
    )

    return {"message": f"JoinNode '{req.name}' added"}

@app.post("/workflow/{workflow_name}/run")
def run_workflow(workflow_name: str):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    wf.last_run_at = datetime.datetime.now()
    wf.failed_nodes = []

    for node in wf.nodes:
        try:
            node.run()
        except Exception:
            wf.failed_nodes.append(node.name)

    if all(n.status == "completed" for n in wf.nodes):
        wf.completed_at = datetime.datetime.now()


    return {
        "message": "Workflow executed",
        "failed_nodes": wf.failed_nodes,
        "last_run_at": wf.last_run_at,
        "completed_at": wf.completed_at
    }

@app.get("/workflow/{workflow_name}/nodes/{node_name}/preview")
def preview_node(workflow_name: str, node_name: str, limit: int = 5):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    node = next((n for n in wf.nodes if n.name == node_name), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    if hasattr(node.output, "fetch"):
        return node.output.fetch(limit).to_dicts()
    elif isinstance(node.output, str) and node.output.endswith(".parquet"):
        df = pl.read_parquet(node.output)
        return df.head(limit).to_dicts()
    else:
        raise HTTPException(status_code=400, detail="Node output not previewable")

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


@app.get("/workflow/{workflow_name}/export")
def export_workflow(workflow_name: str):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return {
        "name": wf.name,
        "created_at": str(wf.created_at),
        "status": wf.status,
        "last_run_at": str(wf.last_run_at) if wf.last_run_at else None,
        "completed_at": str(wf.completed_at) if wf.completed_at else None,
        "failed_nodes": wf.failed_nodes,
        "nodes": [
            {
                "name": n.name,
                "type": n.__class__.__name__,
                "status": n.status,
                "created_at": str(n.created_at),
            }
            for n in wf.nodes
        ]
    }


@app.post("/workflow/{workflow_name}/filter_node")
def add_filter_node(workflow_name: str, req: AddFilterNodeRequest):
    wf = workflows.get(workflow_name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    try:
        expr = eval(req.filter_expr, {"pl": pl}, {})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid filter_expr: {e}")
    wf.add_node(
        FilterNode,
        name=req.name,
        input_table=req.input_table,
        filter_expr=expr
    )

        
    register_action(
        action="add_filter_node",
        workflow=wf.name,
        payload=req.dict()
    )

    return {"message": f"FilterNode '{req.name}' added"}
