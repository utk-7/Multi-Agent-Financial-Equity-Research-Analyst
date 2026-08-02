import asyncio
import time
import logging

logger = logging.getLogger(__name__)

# Global lock to ensure only one LLM request is in-flight across the whole application
_llm_lock = asyncio.Lock()

# Track the last time a request was completed
_last_request_time = 0.0

# Minimum gap in seconds between LLM requests to satisfy 5 Req/Min
MIN_GAP_SECONDS = 15.0

import os
import json
from datetime import datetime

# Path for tracking daily usage
USAGE_FILE = os.path.join(os.path.dirname(__file__), "llm_usage.json")

def _log_usage():
    today = datetime.now().strftime("%Y-%m-%d")
    usage = {}
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r") as f:
                usage = json.load(f)
        except Exception:
            pass
            
    if usage.get("date") != today:
        usage = {"date": today, "count": 0}
        
    usage["count"] += 1
    
    try:
        with open(USAGE_FILE, "w") as f:
            json.dump(usage, f)
    except Exception as e:
        logger.error(f"Failed to log usage: {e}")
        
    logger.info(f"LLM Request Counter: {usage['count']} requests made today.")

async def execute_with_pacing(coroutine_func, *args, **kwargs):
    """
    Executes a coroutine function (like an LLM call) while enforcing a strict global lock
    and a minimum delay since the last call.
    """
    global _last_request_time
    
    async with _llm_lock:
        now = time.time()
        elapsed = now - _last_request_time
        
        if elapsed < MIN_GAP_SECONDS:
            wait_time = MIN_GAP_SECONDS - elapsed
            logger.info(f"Pacing LLM call: waiting {wait_time:.2f} seconds before executing...")
            await asyncio.sleep(wait_time)
            
        try:
            _log_usage()
            logger.info("Executing LLM call...")
            result = await coroutine_func(*args, **kwargs)
            return result
        finally:
            _last_request_time = time.time()
