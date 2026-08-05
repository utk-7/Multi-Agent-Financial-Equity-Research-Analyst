import asyncio
import json
import logging
import os
import tempfile

from dotenv import load_dotenv

# Load environment variables FIRST, before importing any langgraph/langchain modules
load_dotenv(override=True)

from typing import Any, Dict, List

from app.export.pdf_export import export_to_pdf
from app.graph.build_graph import build_equity_research_graph
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        os.getenv("FRONTEND_URL", "https://equity-research-frontend.vercel.app"),
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_equity_research_graph()

# In-memory store to coordinate SSE streams and resumes
active_runs = {}


class RunRequest(BaseModel):
    ticker: str
    run_mode: str = "fast"
    thread_id: str


class ApproveRequest(BaseModel):
    thread_id: str
    red_flags: List[Dict[str, Any]]


class ExportRequest(BaseModel):
    thread_id: str


@app.post("/run")
async def run_graph_endpoint(req: RunRequest):
    thread_id = req.thread_id
    config = {"configurable": {"thread_id": thread_id}}

    resume_event = asyncio.Event()
    active_runs[thread_id] = {"resume_event": resume_event}

    async def event_stream():
        logger.info(f"Starting graph for {req.ticker} in {req.run_mode} mode")
        state = {"ticker": req.ticker, "run_mode": req.run_mode}

        try:
            # Execute up to the interrupt (or completion) using astream_events to capture node progress
            async for event in graph.astream_events(state, config=config, version="v1"):
                kind = event["event"]
                metadata = event.get("metadata", {})

                # Check if it's a node event
                if (
                    kind == "on_chain_start"
                    and metadata.get("langgraph_node")
                    and metadata["langgraph_node"] != "__start__"
                ):
                    node_name = metadata["langgraph_node"]
                    yield f"event: node_started\ndata: {json.dumps({'node': node_name})}\n\n"

                elif (
                    kind == "on_chain_end"
                    and metadata.get("langgraph_node")
                    and metadata["langgraph_node"] != "__start__"
                ):
                    node_name = metadata["langgraph_node"]
                    clean_name = node_name.replace("_", " ").title()
                    yield f"event: node_completed\ndata: {json.dumps({'node': node_name, 'output_summary': f'{clean_name} completed'})}\n\n"

            # Check state snapshot to see if we paused
            state_snap = graph.get_state(config)

            if state_snap.next:
                # Graph paused
                logger.info("Graph interrupted. Emitting interrupt_paused.")
                red_flags = state_snap.values.get("red_flags", [])
                yield f"event: interrupt_paused\ndata: {json.dumps({'red_flags': red_flags})}\n\n"

                # Keep SSE open until /approve sets the event
                logger.info("Holding SSE connection open, waiting for approval...")
                await resume_event.wait()

                logger.info("Resume event triggered. Emitting run_resumed.")
                yield f"event: run_resumed\ndata: {json.dumps({'status': 'resumed'})}\n\n"

            # Get final state from snapshot
            state_snap = graph.get_state(config)
            final_report = state_snap.values.get("final_report", {})
            eval_metrics = state_snap.values.get("eval_metrics", {})
            citations = state_snap.values.get("citations", [])
            ratios = state_snap.values.get("ratios", {})
            dcf_valuation = state_snap.values.get("dcf_valuation", {})

            yield f"event: run_completed\ndata: {json.dumps({'status': 'done', 'final_report': final_report, 'eval_metrics': eval_metrics, 'citations': citations, 'ratio_table': ratios, 'valuation_range': dcf_valuation})}\n\n"

        except Exception as e:
            logger.error(f"Error in graph execution: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
        finally:
            if thread_id in active_runs:
                del active_runs[thread_id]

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/approve")
async def approve_endpoint(req: ApproveRequest):
    thread_id = req.thread_id
    config = {"configurable": {"thread_id": thread_id}}

    logger.info(f"Received approval for thread {thread_id}")

    # 1. Update the state with the edited/approved red flags
    graph.update_state(config, {"red_flags": req.red_flags})

    # 2. Resume the graph by passing None as state payload
    await graph.ainvoke(None, config=config)

    # 3. Notify the waiting SSE stream
    if thread_id in active_runs:
        active_runs[thread_id]["resume_event"].set()

    return {"status": "success", "message": "Graph resumed"}


def cleanup_temp_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.error(f"Failed to cleanup temp file {path}: {e}")


@app.post("/export")
async def export_endpoint(req: ExportRequest, background_tasks: BackgroundTasks):
    config = {"configurable": {"thread_id": req.thread_id}}
    state_snap = graph.get_state(config)

    if not state_snap or not state_snap.values:
        return {"error": "No state found for this thread_id"}

    state_dict = state_snap.values

    # Create temp file
    fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    # Try exporting
    export_to_pdf(state_dict, temp_pdf_path)

    # Check if we got PDF or HTML fallback
    if os.path.exists(temp_pdf_path) and os.path.getsize(temp_pdf_path) > 0:
        file_to_send = temp_pdf_path
        media_type = "application/pdf"
        filename = f"{state_dict.get('ticker', 'Report')}_Equity_Research.pdf"
    else:
        # Check fallback html
        fallback_path = temp_pdf_path.replace(".pdf", ".html")
        if os.path.exists(fallback_path):
            file_to_send = fallback_path
            media_type = "text/html"
            filename = f"{state_dict.get('ticker', 'Report')}_Equity_Research.html"
            background_tasks.add_task(
                cleanup_temp_file, temp_pdf_path
            )  # Cleanup empty pdf
        else:
            return {"error": "Failed to generate report file"}

    background_tasks.add_task(cleanup_temp_file, file_to_send)

    return FileResponse(
        path=file_to_send,
        media_type=media_type,
        filename=filename,
        headers={"Access-Control-Expose-Headers": "Content-Disposition"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
