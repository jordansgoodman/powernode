# PowerNode

PowerNode is a low-code data analytics platform built with Polars, FastAPI, React, and Tailwind CSS.

You can use it to build, preview, and execute data workflows using a simple node-based interface.

GitHub: [https://github.com/jordansgoodman/powernode](https://github.com/jordansgoodman/powernode)

---

## Features

- Node-based workflows for building ETL pipelines
- Fast, efficient data processing with Polars
- Low-code interface with support for CSV, Parquet, and SQLite
- FastAPI backend with a REST API for workflow and node management
- React + Tailwind frontend for a clean, responsive UI
- Local-first: everything runs and stores locally

---

## Quick Start

> This project is under active development.
```bash
git clone https://github.com/jordansgoodman/powernode.git
cd powernode
```

# Set up backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Example Workflow

1. Create a new workflow
2. Add CSV-reading nodes
3. Join datasets on shared keys
4. Filter rows based on expressions
5. Preview or export the result to Parquet

You can use the workflow_runner.py script to test commands against the API.

