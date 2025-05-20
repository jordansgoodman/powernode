import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getWorkflows, createWorkflow } from "../api";

function Workflows() {
  const [workflows, setWorkflows] = useState([]);
  const [name, setName] = useState("");

  useEffect(() => {
    refresh();
  }, []);

  async function refresh() {
    const data = await getWorkflows();
    setWorkflows(data);
  }

  async function handleCreate(e) {
    e.preventDefault();
    if (!name.trim()) return;
    await createWorkflow(name);
    setName("");
    refresh();
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">PowerNode Workflows</h1>

      <form onSubmit={handleCreate} className="flex gap-2">
        <input
          type="text"
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="Enter new workflow name"
          className="flex-1 border border-gray-300 px-3 py-2 rounded focus:outline-none focus:ring focus:border-blue-500"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Create
        </button>
      </form>

      <ul className="space-y-2">
        {workflows.map(wf => (
          <li
            key={wf.name}
            className="border p-4 rounded bg-white shadow-sm hover:bg-gray-50 transition"
          >
            <Link to={`/workflow/${wf.name}`} className="block">
              <div className="font-semibold text-lg text-blue-600">{wf.name}</div>
              <div className="text-sm text-gray-500">
                Status: {wf.status} | Last Run: {wf.last_run_at || "—"}
              </div>
              {wf.failed_nodes?.length > 0 && (
                <div className="text-sm text-red-600 mt-1">
                  Failed Nodes: {wf.failed_nodes.join(", ")}
                </div>
              )}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Workflows;
