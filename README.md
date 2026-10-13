# Campus Customs HW 5

Campus Customs is a local shop operations desk with a FastMCP server, a FastAPI multi-agent backend, and a React dashboard. The agents use MCP for shop facts and prepare actions for human review. They do not contact real vendors or customers.

## Project layout

```text
AI_prompts.md
requirements.txt
.env.example
.gitignore
.mcp.json
README.md
data/campus_customs.db
data/campus_customs_new.db
mcp_server/server.py
mcp_server/README.md
backend/main.py
backend/models.py
backend/prompts/
frontend/
output/
```

The original database is `data/campus_customs.db`. The working database is `data/campus_customs_new.db`.

## Clean run

Before a full three-ticket run, restore the working copy from the original database.

```bash
cp data/campus_customs.db data/campus_customs_new.db
```

The backend also exposes `POST /reset` for this operation.

## Install dependencies

Create a local environment and install the Python dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

Copy `.env.example` to `.env` and add the Portkey API key locally. Never commit `.env` or any secret key. The application is configured for Portkey with only `gpt-6-luna`.

## Start the MCP server

The backend launches the MCP server over stdio through `.mcp.json`. To run the server directly for an MCP client, use the project root and run:

```bash
python3 mcp_server/server.py
```

## Start the FastAPI backend

In a terminal from the `backend` folder, run:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The backend serves the dashboard API at `http://localhost:8000` and permits the Vite origin `http://localhost:5173`.

## Start the React board

In another terminal from the project root, run:

```bash
cd frontend
npm run dev
```

Open the Vite URL shown in the terminal, normally `http://localhost:5173`.

## Resolve the three tickets

1. Reset the working database before the full run with `POST http://localhost:8000/reset`, or copy the original database over the working copy with the command above.
2. Confirm the starting checking balance on the board.
3. Run Tickets 101, 102, and 103 from the dashboard.
4. Review agent recommendations and draft communications.
5. Approve payments only through the dashboard when appropriate. The approval route updates the relevant payment table and cash balance, refuses insufficient funds, and never allows a negative balance.
6. Ticket 103 must remain blocked if the proposed purchase exceeds available cash.

All communications stay as drafts. No real vendor or customer email or call is made.

## Outputs

The `output/` folder contains the schema and harness documentation, MCP smoke evidence, audit trail, dashboard design notes, ticket planning board, resolved-ticket summary, and resolved board snapshot.

