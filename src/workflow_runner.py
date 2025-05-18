import requests

BASE_URL = "http://127.0.0.1:8000"
WORKFLOW_NAME = "test_read_csv"

requests.delete(f"{BASE_URL}/workflow/{WORKFLOW_NAME}")

def safe_post(endpoint, payload):
    resp = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    try:
        return resp.status_code, resp.json()
    except:
        return resp.status_code, resp.text


code, msg = safe_post("/workflow", {"name": WORKFLOW_NAME})
print("Create workflow:", code, msg)


# todo: this should be handled better, via API
for name, file in [
    ("read_sales", "testdataset/Sales.csv"),
    ("read_features", "testdataset/Features.csv"),
    ("read_stores", "testdataset/Stores.csv")
]:
    code, msg = safe_post(f"/workflow/{WORKFLOW_NAME}/read_node", {
        "name": name,
        "file_path": file
    })
    print(f"Add node {name}:", code, msg)


# todo: this should be handled better - via API
code, msg = safe_post(f"/workflow/{WORKFLOW_NAME}/join_node", {
    "name": "join_sales_features",
    "left_table": "read_sales",
    "right_table": "read_features",
    "on": ["Store", "Date"],
    "how": "inner"
})
print("Add join node:", code, msg)

code, msg = safe_post(f"/workflow/{WORKFLOW_NAME}/run", {})
print("Run workflow:", code, msg)

preview = requests.get(f"{BASE_URL}/workflow/{WORKFLOW_NAME}/nodes/join_sales_features/preview", params={"limit": 5})
print("\nPreview Output:")
print(preview.json())
