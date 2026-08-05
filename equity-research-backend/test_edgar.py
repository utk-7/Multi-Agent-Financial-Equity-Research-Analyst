import asyncio
from app.connectors.edgar_client import fetch_10k_text

async def main():
    risk_factors, mda = await fetch_10k_text("MSFT")
    
    if risk_factors:
        print(f"MSFT Risk Factors extracted. Length: {len(risk_factors)} chars.")
    else:
        print("Failed to extract MSFT Risk Factors.")

    if mda:
        print(f"MSFT MD&A extracted. Length: {len(mda)} chars.")
    else:
        print("Failed to extract MSFT MD&A.")

if __name__ == "__main__":
    asyncio.run(main())
