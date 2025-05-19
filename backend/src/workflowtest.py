from workflow import Workflow
from node import ReadCSVNode
from node import JoinNode

wf = Workflow(name="test_read_csv")

sales_node = wf.add_node(
    ReadCSVNode,
    name="read_sales",
    file_path="testdataset/Sales.csv"
)

features_node = wf.add_node(
    ReadCSVNode,
    name="read_features",
    file_path="testdataset/Features.csv"
)

stores_node = wf.add_node(
    ReadCSVNode,
    name="read_stores",
    file_path="testdataset/Stores.csv"
)

join_node = wf.add_node(
    JoinNode,
    name="join_sales_features",
    left_table="read_sales",
    right_table="read_features",
    on=["Store", "Date"],
    how="inner"
)

sales_node.run()
features_node.run()
stores_node.run()
join_node.run()

df = join_node.output.fetch(5)

print(df)
