const BASE_URL = "http://127.0.0.1:8000";

export async function getWorkflows() {
  const res = await fetch(`${BASE_URL}/workflows`);
  return await res.json();
}

export async function createWorkflow(name) {
  const res = await fetch(`${BASE_URL}/workflow`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  return await res.json();
}
