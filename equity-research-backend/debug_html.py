import asyncio
import re

import httpx
from app.connectors.edgar_client import _get_cik, get_headers
from bs4 import BeautifulSoup


async def debug_html2():
    client = httpx.AsyncClient(headers=get_headers())
    cik = await _get_cik(client, "MSFT")
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    data = (await client.get(url)).json()
    forms = data["filings"]["recent"]["form"]
    i = forms.index("10-K")
    doc = data["filings"]["recent"]["primaryDocument"][i]
    acc = data["filings"]["recent"]["accessionNumber"][i].replace("-", "")

    resp = await client.get(
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}"
    )
    html = resp.text

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["span", "font", "b", "i", "u", "a", "strong", "em"]):
        tag.unwrap()
    soup.smooth()

    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n+", "\n", text)

    # Check if RIS K is fixed
    idx = text.find("RISK FACTORS")
    if idx != -1:
        print("Found clean text snippet:", repr(text[idx - 20 : idx + 50]))
    else:
        print("Not found! Let's see what we got around ITEM 1A:")
        idx = text.find("ITEM 1A")
        print(repr(text[idx : idx + 100]))


asyncio.run(debug_html2())
