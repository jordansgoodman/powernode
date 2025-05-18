import requests

BASE_URL = "http://127.0.0.1:8000"
WORKFLOW_NAME = "test_read_csv"

# 1. Create the workflow
r = requests.post(f"{BASE_URL}/workflow", json={"name": WORKFLOW_NAME})
print("Workflow create:", r.status_code, r.json())

# 2. Add ReadCSVNode: sales
r = requests.post(f"{BASE_URL}/workflow/{WORKFLOW_NAME}/read_node", json={
    "name": "read_sales",
    "file_path": "testdataset/Sales.csv"
})
print("Add read_sales:", r.status_code, r.json())

# 3. Add ReadCSVNode: features
r = requests.post(f"{BASE_URL}/workflow/{WORKFLOW_NAME}/read_node", json={
    "name": "read_features",
    "file_path": "testdataset/Features.csv"
})
print("Add read_features:", r.status_code, r.json())

# 4. Add ReadCSVNode: stores
r = requests.post(f"{BASE_URL}/workflow/{WORKFLOW_NAME}/read_node", json={
    "name": "read_stores",
    "file_path": "testdataset/Stores.csv"
})
print("Add read_stores:", r.status_code, r.json())

# 5. Add JoinNode
r = requests.post(f"{BASE_URL}/workflow/{WORKFLOW_NAME}/join_node", json={
    "name": "join_sales_features",
    "left_table": "read_sales",
    "right_table": "read_features",
    "on": ["Store", "Date"],
    "how": "inner"
})
print("Add join_sales_features:", r.status_code, r.json())

# 6. Run the workflow
r = requests.post(f"{BASE_URL}/workflow/{WORKFLOW_NAME}/run")
print("Run workflow:", r.status_code, r.json())

# 7. Preview output from join node
r = requests.get(f"{BASE_URL}/workflow/{WORKFLOW_NAME}/nodes/join_sales_features/preview", params={"limit": 5})
print("\nPreview join_sales_features:")
for row in r.json():
    print(row)
