import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

const BASE_URL = "http://127.0.0.1:8000";

function WorkflowDetail() {
  const { name } = useParams();
  const [nodes, setNodes] = useState([]);
  const [filePath, setFilePath] = useState("");
  const [preview, setPreview] = useState([]);

  async function refresh() {
    const res = await fetch(`${BASE_URL}/workflow/${name}/nodes`);
    const data = await res.json();
    setNodes(data);
  }

  async function addReadNode() {
    const res = await fetch(`${BASE_URL}/workflow/${name}/read_node`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: `read_${Date.now()}`,
        file_path: filePath,
      }),
    });
    setFilePath("");
    refresh();
  }

  async function runWorkflow() {
    await fetch(`${BASE_URL}/workflow/${name}/run`, {
      method: "POST",
    });
    refresh();
  }

  async function previewJoin() {
    const node = nodes.find(n => n.type === "JoinNode");
    if (!node) return;
    const res = await fetch(`${BASE_URL}/workflow/${name}/nodes/${node.name}/preview?limit=5`);
    const data = await res.json();
    setPreview(data);
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">Workflow: {name}</h1>

      <div className="space-y-2">
        <input
          type="text"
          value={filePath}
          onChange={e => setFilePath(e.target.value)}
          placeholder="testdataset/Sales.csv"
          className="border px-3 py-2 w-full rounded"
        />
        <button
          onClick={addReadNode}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Add ReadCSV Node
        </button>
      </div>

      <button
        onClick={runWorkflow}
        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
      >
        Run Workflow
      </button>

      <button
        onClick={previewJoin}
        className="bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-800"
      >
        Preview Join Output
      </button>

      <h2 className="text-xl font-semibold mt-6">Nodes</h2>
      <ul className="space-y-2">
        {nodes.map(node => (
          <li key={node.name} className="border p-4 rounded bg-white shadow-sm">
            <div className="font-semibold">{node.name}</div>
            <div className="text-sm text-gray-500">{node.type} | {node.status}</div>
          </li>
        ))}
      </ul>

      {preview.length > 0 && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold">Preview Output</h2>
          <pre className="text-sm bg-gray-100 p-4 overflow-auto rounded">{JSON.stringify(preview, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default WorkflowDetail;
