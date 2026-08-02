import httpx
import re
import os
import logging
from bs4 import BeautifulSoup
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def get_headers():
    user_agent = os.getenv("SEC_EDGAR_USER_AGENT", "Student Research utkch@example.com")
    return {
        "User-Agent": user_agent,
        "Accept-Encoding": "gzip, deflate"
    }

async def fetch_10k_text(ticker: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        async with httpx.AsyncClient(headers=get_headers(), timeout=10.0) as client:
            cik = await _get_cik(client, ticker)
            if not cik:
                logger.error(f"Could not find CIK for ticker {ticker}")
                return None, None
                
            submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            resp = await client.get(submissions_url)
            resp.raise_for_status()
            data = resp.json()
            
            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            accessions = recent.get("accessionNumber", [])
            primary_docs = recent.get("primaryDocument", [])
            
            doc_url = None
            for i, form in enumerate(forms):
                if form == "10-K":
                    accession = accessions[i].replace("-", "")
                    doc_name = primary_docs[i]
                    doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{doc_name}"
                    break
                    
            if not doc_url:
                logger.error(f"Could not find a 10-K filing for {ticker}")
                return None, None
                
            doc_resp = await client.get(doc_url)
            doc_resp.raise_for_status()
            raw_html = doc_resp.text
            
            return _extract_sections(raw_html)
    except Exception as e:
        logger.error(f"Error fetching 10-K for {ticker} from SEC EDGAR: {e}")
        return None, None

async def _get_cik(client: httpx.AsyncClient, ticker: str) -> Optional[str]:
    resp = await client.get("https://www.sec.gov/files/company_tickers.json")
    resp.raise_for_status()
    data = resp.json()
    for _, info in data.items():
        if info.get("ticker") == ticker:
            return str(info.get("cik_str")).zfill(10)
    return None

def _extract_sections(raw_html: str) -> Tuple[Optional[str], Optional[str]]:
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # Unwrap inline tags to prevent them from introducing spurious separators/newlines mid-word
    for tag in soup.find_all(['span', 'font', 'b', 'i', 'u', 'a', 'strong', 'em']):
        tag.unwrap()
    soup.smooth()
    
    text = soup.get_text(separator='\n', strip=True)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    
    risk_factors_pattern = r"(?i)Item\s+1A\."
    risk_factors_next = r"(?i)Item\s+1B\."
    
    mda_pattern = r"(?i)Item\s+7\."
    mda_next = r"(?i)Item\s+7A\."
    
    risk_factors = _extract_section_robust(text, risk_factors_pattern, risk_factors_next)
    mda = _extract_section_robust(text, mda_pattern, mda_next)
    
    return risk_factors, mda

def _extract_section_robust(text: str, start_pattern: str, end_pattern: str, max_length: int = 20000) -> Optional[str]:
    starts = [m for m in re.finditer(start_pattern, text)]
    ends = [m for m in re.finditer(end_pattern, text)]
    
    best_text = None
    max_gap = 0
    
    for start_match in starts:
        start_idx = start_match.start()
        
        # find the next end_pattern that occurs after this start_match
        next_end = None
        for end_match in ends:
            if end_match.start() > start_idx:
                next_end = end_match.start()
                break
                
        # if we found an end, compute the distance
        if next_end:
            gap = next_end - start_idx
            if gap > max_gap:
                max_gap = gap
                best_text = text[start_idx:next_end]
        else:
            # if no end found after this start, maybe it's the last section (rare but possible)
            gap = len(text) - start_idx
            if gap > max_gap:
                max_gap = gap
                best_text = text[start_idx:start_idx + max_length]
                
    if best_text and max_gap > 1000:
        # Cap the length
        return best_text[:max_length]
        
    return None
