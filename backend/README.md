# SonsOfTuring

This is a project to manage agents AI. It permits create agents by configurations setted previouslly.

# To run this app:

use uv to resolve dependencies:

```bash
cd backend
uv sync
```

Run the server:

```bash
PYTHONPATH=src uv run uvicorn src.main:app --reload
```
