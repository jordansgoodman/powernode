import requests

BASE_URL = "http://127.0.0.1:8000"
WORKFLOW_NAME = "test_read_csv"

def safe_post(endpoint, payload=None):
    resp = requests.post(f"{BASE_URL}{endpoint}", json=payload or {})
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, resp.text

def safe_get(endpoint, params=None):
    resp = requests.get(f"{BASE_URL}{endpoint}", params=params or {})
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, resp.text

def safe_delete(endpoint):
    resp = requests.delete(f"{BASE_URL}{endpoint}")
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, resp.text

def line():
    print("-" * 50)

# Delete workflow if it exists
code, msg = safe_delete(f"/workflow/{WORKFLOW_NAME}")
print("Delete workflow:", code, msg)
line()

# Create workflow
code, msg = safe_post("/workflow", {"name": WORKFLOW_NAME})
print("Create workflow:", code, msg)
line()

# Add ReadCSVNodes
read_nodes = {
    "read_sales": "testdataset/Sales.csv",
    "read_features": "testdataset/Features.csv",
    "read_stores": "testdataset/Stores.csv"
}
for name, path in read_nodes.items():
    code, msg = safe_post(f"/workflow/{WORKFLOW_NAME}/read_node", {
        "name": name,
        "file_path": path
    })
    print(f"Add ReadCSVNode {name}:", code, msg)
line()

# Add JoinNode
code, msg = safe_post(f"/workflow/{WORKFLOW_NAME}/join_node", {
    "name": "join_sales_features",
    "left_table": "read_sales",
    "right_table": "read_features",
    "on": ["Store", "Date"],
    "how": "inner"
})
print("Add JoinNode:", code, msg)
line()

# Run entire workflow
code, msg = safe_post(f"/workflow/{WORKFLOW_NAME}/run")
print("Run workflow:", code, msg)
line()

# Run a specific node
code, msg = safe_post(f"/workflow/{WORKFLOW_NAME}/nodes/join_sales_features/run")
print("Run single node (join_sales_features):", code, msg)
line()


# Preview a node output
code, msg = safe_get(f"/workflow/{WORKFLOW_NAME}/nodes/join_sales_features/preview", params={"limit": 5})
print("Preview output:", code)
for row in msg:
    print(row)
line()

# List all workflows
code, msg = safe_get("/workflows")
print("List all workflows:", code)
for wf in msg:
    print(wf)
line()

# List nodes in workflow

code, msg = safe_get(f"/workflow/{WORKFLOW_NAME}/nodes")
print("List nodes in workflow:", code)
for node in msg:
    print(node)
line()

# Export workflow metadata
code, msg = safe_get(f"/workflow/{WORKFLOW_NAME}/export")
print("Export metadata:", code)
print(msg)
line()

# filter

#todo: add abstract filter logic - detect columns 
code, msg = safe_post(f"/workflow/{WORKFLOW_NAME}/filter_node", {
    "name": "filter_holidays",
    "input_table": "join_sales_features",
    "filter_expr": "pl.col('IsHoliday_right') == True"
})
print("Add FilterNode:", code, msg)




