import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.graph.nodes.ingestion import run_ingestion_node

def test_ticker(ticker: str):
    print(f"\n{'='*50}\nTesting Ingestion Node for: {ticker}\n{'='*50}")
    result = run_ingestion_node(ticker)
    
    print("\n--- Fundamentals ---")
    if result["fundamentals"]:
        for k, v in result["fundamentals"].model_dump().items():
            print(f"{k}: {v}")
    
    print("\n--- EDGAR Text Extraction ---")
    rf = result["risk_factors_text"]
    mda = result["mda_text"]
    print(f"Risk Factors length: {len(rf) if rf else 0} chars")
    print(f"MD&A length: {len(mda) if mda else 0} chars")
    
    if rf:
        print("\nRisk Factors Preview (first 200 chars):")
        print(rf[:200].replace('\n', ' '))
    
    if mda:
        print("\nMD&A Preview (first 200 chars):")
        print(mda[:200].replace('\n', ' '))
        
    print("\n--- Injection Screen ---")
    print(f"Flagged: {result['injection_screen_result'].flagged}")
    print(f"Matched patterns: {result['injection_screen_result'].matched_patterns}")

if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    
    test_ticker("AAPL")
    test_ticker("MSFT")
