from fastapi import FastAPI
import api.routing as routing
import uvicorn

app = FastAPI(
    title="FES-API",
    description="This is a FastAPI application for the FES (Functional Engine Server) API.",
    version="2.0.0",
)

app.include_router(routing.templates_router, prefix="/api/templates", tags=["Templates"])
app.include_router(routing.workflows_router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(routing.outputs_router, prefix="/api/workflows/download", tags=["Workflow downloads"])

import api.database as database


# database.init_db()

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)