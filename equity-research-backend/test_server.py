import asyncio
import json

import httpx


async def test_fast_mode():
    print("\n=== Testing Fast Mode ===")
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream(
            "POST",
            "http://127.0.0.1:8000/run",
            json={"ticker": "AAPL", "run_mode": "fast", "thread_id": "test_fast"},
        ) as response:
            async for line in response.aiter_lines():
                if line.strip():
                    print(line)


async def test_verified_mode():
    print("\n=== Testing Verified Mode ===")
    async with httpx.AsyncClient(timeout=300) as client:
        async with client.stream(
            "POST",
            "http://127.0.0.1:8000/run",
            json={
                "ticker": "AAPL",
                "run_mode": "verified",
                "thread_id": "test_verified",
            },
        ) as response:
            async for line in response.aiter_lines():
                if line.strip():
                    print(line)

                # If we hit interrupt_paused, we simulate the user hitting /approve
                if "interrupt_paused" in line:
                    print("--> Server paused. Sending /approve request...")
                    # Send approve in a background task so we keep reading the stream
                    asyncio.create_task(send_approve())


async def send_approve():
    await asyncio.sleep(2)  # simulate user delay
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "http://127.0.0.1:8000/approve",
            json={
                "thread_id": "test_verified",
                "red_flags": [
                    {
                        "flagged": True,
                        "type": "Test Flag",
                        "severity": "low",
                        "description": "Human approved flag",
                        "source": "human",
                    }
                ],
            },
        )
        print(f"--> /approve response: {resp.status_code} - {resp.json()}")


async def main():
    await test_verified_mode()


if __name__ == "__main__":
    asyncio.run(main())
