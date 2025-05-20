# TODO

1. Project initialization
   1. Create monorepo with `backend/`, `frontend/`, `.gitignore`, `README.md`
   2. In `backend/`, set up FastAPI, Polars (or DuckDB), project layout, virtual environment, and CI configurations
   3. In `frontend/`, set up React, TypeScript, Tailwind CSS, ESLint/Prettier, and build scripts

2. Core data model and API contracts
   1. Define a JSON schema for workflows (nodes, connections, node configs, layout)
   2. Implement Pydantic models for Node, Connection, Workflow
   3. Expose CRUD endpoints:
      1. `GET /workflows`
      2. `POST /workflows`
      3. `GET /workflows/{id}`
      4. `PUT /workflows/{id}`
      5. `DELETE /workflows/{id}`

3. Frontend state management and loading
   1. Choose a state library (Redux Toolkit, Zustand, or Context API)
   2. Create stores for current workflow, node palette, and UI state
   3. On startup, fetch saved workflows and allow selecting or creating new

4. Node palette and registration
   1. Define a registry of available node types (ReadCSV, Filter, Join, etc.) with metadata (icon, default config)
   2. Implement `Sidebar.tsx` that lists node types and supports drag-and-drop

5. Canvas with drag-and-drop placement
   1. Create `Canvas.tsx` that accepts drops, computes drop coordinates, and instantiates nodes in state
   2. Implement node movement with mouse-down, mouse-move, and mouse-up handlers
   3. Persist node positions in the workflow state

6. Connections between nodes
   1. Add connection “handles” on hover for each node
   2. Capture first and second handle clicks to create a connection record
   3. Render connections as SVG `<line>` or `<path>` elements between node anchor points

7. Node configuration panel
   1. Build a side panel or modal that opens when a node is selected
   2. Dynamically render form fields based on the node’s config schema
   3. Validate and save the config back into the node state

8. Workflow persistence and versioning
   1. Wire save/load buttons to the CRUD API
   2. Implement automatic autosave or manual save reminders
   3. Support version history or simple snapshots of workflow JSON

9. Execution engine core
   1. In the backend, write a runner that:
      1. Validates the graph (no unintended cycles)
      2. Topologically sorts nodes
      3. Executes each node in order, passing DataFrame or table outputs forward
   2. Expose endpoints:
      1. `POST /workflows/{id}/run`
      2. `GET /workflows/{id}/status`
      3. `GET /workflows/{id}/results/{nodeId}`

10. Sample node implementations
    1. ReadCSV node: load a CSV into a Polars or DuckDB table
    2. Filter node: apply row filters using user-configured expressions
    3. Join node: perform inner/left/right joins on two upstream node outputs
    4. GroupBy/Aggregate node: grouping and aggregation functions

11. Data preview and debugging
    1. After running, fetch a preview of each node’s output (first N rows) via API
    2. Display previews in a pop-up or panel when the user clicks a node
    3. Surface execution logs, errors, and timings in a console view

12. Undo/redo and history
    1. Implement an action history stack in the frontend state
    2. Record add/remove/move/configure actions
    3. Provide Undo and Redo controls

13. Composite and loop constructs
    1. Enable grouping of nodes into a composite “meta-node” with its own sub-canvas
    2. Implement loop start and loop end nodes that iterate over collections or parameter sets

14. Flow variables and global parameters
    1. Define workflow-level variables that can be referenced by node configs
    2. Build a UI for defining and editing flow variables
    3. Inject variable values when executing nodes

15. Extensibility and custom nodes
    1. Create a plugin interface for new node types (Python entry point, metadata)
    2. Dynamically load available plugins at backend startup
    3. Update the frontend registry when new node types are discovered

16. Visualization nodes
    1. Chart node: render bar/line/pie charts from tabular data
    2. Table node: display full tables with pagination and sorting
    3. Configure chart options in the node config panel

17. Workflow scheduling and deployment
    1. Add support for scheduled runs (cron expressions) in the backend
    2. Persist schedules and trigger workflow execution automatically
    3. Expose schedule management UI in the frontend

18. Collaboration and sharing
    1. Integrate Git or database-backed version control for workflows
    2. Allow users to share workflows via link or export/import JSON
    3. Implement role-based access control (view, edit, run)

19. Testing and quality assurance
    1. Write unit tests for each node type and the execution engine
    2. Add end-to-end tests that create, save, run, and preview a simple workflow
    3. Implement linting or static analysis on workflows to catch misconfigured nodes

20. Performance and scaling
    1. Profile execution times and bottlenecks in the runner
    2. Enable parallel execution of independent branches
    3. Support distributed execution (e.g. using Dask or a job queue)