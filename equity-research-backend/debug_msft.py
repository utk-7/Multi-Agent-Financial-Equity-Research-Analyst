import asyncio
import re
from bs4 import BeautifulSoup
import httpx
from app.connectors.edgar_client import _get_cik, get_headers

async def debug_msft():
    client = httpx.AsyncClient(headers=get_headers())
    cik = await _get_cik(client, 'MSFT')
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    data = (await client.get(url)).json()
    forms = data['filings']['recent']['form']
    i = forms.index('10-K')
    doc = data['filings']['recent']['primaryDocument'][i]
    acc = data['filings']['recent']['accessionNumber'][i].replace('-', '')
    
    resp = await client.get(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}")
    text = BeautifulSoup(resp.text, 'html.parser').get_text(separator='\n', strip=True)
    text = re.sub(r'\n+', '\n', text)
    
    print("All generic matches for Item 1A:")
    for m in re.finditer(r"(?i)Item\s+1A", text):
        idx = m.start()
        print(repr(text[idx:idx+50].replace('\n', '\\n')))
        
asyncio.run(debug_msft())
