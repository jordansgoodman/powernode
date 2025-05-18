from workflow import Workflow
from node import ReadCSVNode

wf = Workflow(name="customer_analysis")
print(wf)
# read_orders = wf.add_node(ReadCSVNode, name="read_orders", file_path="data/orders.csv")

