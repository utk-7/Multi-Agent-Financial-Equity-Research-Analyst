import re
from app.schemas.models import InjectionScreenResult

SUSPICIOUS_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt",
    r"you are now",
    r"<instructions>",
    r"print all instructions",
    r"forget previous",
]

def screen_text(text: str) -> InjectionScreenResult:
    if not text:
        return InjectionScreenResult(flagged=False, matched_patterns=[])
        
    matched = []
    text_lower = text.lower()
    
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text_lower):
            matched.append(pattern)
            
    return InjectionScreenResult(
        flagged=len(matched) > 0,
        matched_patterns=matched
    )
