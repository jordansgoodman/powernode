# About

Powernode is a low-code data analytics tool powered by Polars, FastAPI, React and Tailwind CSS.

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
```
git clone https://github.com/jordansgoodman/powernode.git
cd powernode
```

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# In another terminal: set up frontend
cd ../frontend
npm install
npm run dev

## Example Workflow

Create a new workflow

Add CSV-reading nodes

Join datasets on shared keys

Filter rows based on expressions

Preview or export the result to Parquet

You can use the workflow_runner.py script to test commands against the API.

