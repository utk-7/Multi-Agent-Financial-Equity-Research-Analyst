import datetime
import subprocess
import sys
import time

start_time = datetime.datetime.now()
deadline = start_time + datetime.timedelta(minutes=14)  # 14 more mins (total 20)

while datetime.datetime.now() < deadline:
    print(f"[{datetime.datetime.now()}] Polling graph for AAPL...")

    # Just run for AAPL to save time, we can modify run_graph.py to take args or just run it.
    # Actually run_graph.py runs both, which is fine.
    result = subprocess.run(
        [r".\venv\Scripts\python.exe", "run_graph.py"], capture_output=True, text=True
    )
    print(result.stdout)
    print(result.stderr)

    if (
        '"call_succeeded": true' in result.stdout
        or '"call_succeeded": true' in result.stderr
    ):
        print("SUCCESS! API Key is funded and working.")
        sys.exit(0)
    elif (
        "Your credit balance is too low" in result.stdout
        or "Your credit balance is too low" in result.stderr
    ):
        print("Still 400 Insufficient Funds. Waiting 60 seconds...")
        time.sleep(60)
    else:
        print("Unknown error occurred.")
        time.sleep(60)

print("TIMEOUT: 15 minutes passed with no success.")
sys.exit(1)
