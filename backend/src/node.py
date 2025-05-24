import uuid
import os
import datetime
import polars as pl
import shutil


class Node:
    """Nodes are intialized through Workflows."""
    def __init__(self, name, workflow_path):
        self.id = str(uuid.uuid4())
        self.name = name
        self.created_at = datetime.datetime.now()
        self.status = "idle"
        self.inputs = []
        self.output = None
        self.func = None

        self.path = os.path.join(workflow_path, self.name)
        os.makedirs(self.path, exist_ok=True)

    def delete(self):
        """Delete this node's folder and all contents."""
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

class ReadCSVNode(Node):
    def __init__(self, name, workflow_path, file_path, table_name=None):
        super().__init__(name, workflow_path)

        if not os.path.isabs(file_path):
            root_dir = os.path.abspath(os.path.join(workflow_path, "..", ".."))
            file_path = os.path.join(root_dir, file_path)

        self.file_path = file_path
        self.table_name = table_name or name

    def run(self):
        self.status = "running"
        try:
            lazy_df = pl.read_csv(
                self.file_path,
                ignore_errors=True,
                infer_schema_length=10000
            ).lazy()

            parquet_path = os.path.join(self.path, f"{self.table_name}.parquet")
            lazy_df.sink_parquet(parquet_path, compression="zstd")

            self.output = parquet_path
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            raise e
    
class JoinNode(Node):
    def __init__(self, name, workflow_path, left_table, right_table, on, how="inner"):
        super().__init__(name, workflow_path)
        self.left_table = left_table
        self.right_table = right_table
        self.on = on if isinstance(on, list) else [on]
        self.how = how.lower()
        self.table_name = name 

    def _get_parquet_path(self, table_name):
        node_root = os.path.abspath(os.path.join(self.path, "..", table_name))
        return os.path.join(node_root, f"{table_name}.parquet")

    def run(self):
        self.status = "running"
        try:
            left_path = self._get_parquet_path(self.left_table)
            right_path = self._get_parquet_path(self.right_table)

            left_df = pl.read_parquet(left_path).lazy()
            right_df = pl.read_parquet(right_path).lazy()

            joined = left_df.join(
                right_df,
                on=self.on,
                how=self.how
            )

            parquet_path = os.path.join(self.path, f"{self.table_name}.parquet")
            joined.sink_parquet(parquet_path, compression="zstd")

            self.output = joined
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            raise e


class FilterNode(Node):
    def __init__(self, name, workflow_path, input_table, filter_expr, table_name=None):
        """
        input_table: the name of an earlier node whose output you want to filter
        filter_expr: a polars.Expr, e.g. pl.col("Quantity") > 10
        """
        super().__init__(name, workflow_path)
        self.input_table = input_table
        self.filter_expr = filter_expr
        self.table_name = table_name or name

    def _get_parquet_path(self, table_name):

        node_root = os.path.abspath(os.path.join(self.path, "..", table_name))
        return os.path.join(node_root, f"{table_name}.parquet")

    def run(self):
        self.status = "running"
        try:
            in_path = self._get_parquet_path(self.input_table)
            lf = pl.read_parquet(in_path).lazy()
            filtered = lf.filter(self.filter_expr)
            out_path = os.path.join(self.path, f"{self.table_name}.parquet")
            filtered.sink_parquet(out_path, compression="zstd")
            self.output = filtered
            self.status = "completed"
        except Exception:
            self.status = "failed"
            raise
