import asyncio
import json
import logging
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List
from dotenv import load_dotenv

from app.graph.build_graph import build_equity_research_graph

# Load environment variables
load_dotenv(override=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
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
            # Execute up to the interrupt (or completion)
            await graph.ainvoke(state, config=config)
            
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
            
            yield f"event: run_completed\ndata: {json.dumps({'status': 'done', 'final_report': final_report, 'eval_metrics': eval_metrics, 'citations': citations})}\n\n"
            
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
