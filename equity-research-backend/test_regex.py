import re
from bs4 import BeautifulSoup
import httpx
from app.connectors.edgar_client import _get_cik, get_headers, _extract_section_robust
import asyncio

async def test_regex():
    client = httpx.AsyncClient(headers=get_headers())
    
    for ticker in ["AAPL", "MSFT"]:
        print(f"\n--- {ticker} ---")
        cik = await _get_cik(client, ticker)
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        data = (await client.get(url)).json()
        forms = data['filings']['recent']['form']
        i = forms.index('10-K')
        doc = data['filings']['recent']['primaryDocument'][i]
        acc = data['filings']['recent']['accessionNumber'][i].replace('-', '')
        
        resp = await client.get(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}")
        text = BeautifulSoup(resp.text, 'html.parser').get_text(separator='\n', strip=True)
        text = re.sub(r'\n+', '\n', text)
        
        risk_factors_pattern = r"(?i)Item\s+1A\."
        risk_factors_next = r"(?i)Item\s+1B\."
        
        mda_pattern = r"(?i)Item\s+7\."
        mda_next = r"(?i)Item\s+7A\."
        
        rf = _extract_section_robust(text, risk_factors_pattern, risk_factors_next)
        mda = _extract_section_robust(text, mda_pattern, mda_next)
        
        print("Risk Factors:", repr(rf[:200].replace('\n', ' ')) if rf else "None")
        print("MDA:", repr(mda[:200].replace('\n', ' ')) if mda else "None")

asyncio.run(test_regex())
