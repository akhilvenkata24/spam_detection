import re

def parse_heuristics(text: str) -> dict:
    """
    Stage 1: Heuristic Analysis (fast regex + keyword rules)
    Returns a dict with:
      - score: int (0-100)
      - triggers: list of matching string patterns/reasons
    """
    score = 0
    triggers = []
    
    text_lower = text.lower()
    
    # Define our patterns and scores
    # 1. Urgency
    urgency_patterns = [
        r'\burgent\b', r'\bimmediately\b', r'\bact now\b', 
        r'\blimited time\b', r'\bexpires soon\b', 
        r'\baccount suspended\b', r'\bverify now\b'
    ]
    for pattern in urgency_patterns:
        if re.search(pattern, text_lower):
            score += 15
            triggers.append("urgency")
            break # Avoid over-penalizing multiple urgency words
            
    # 2. Prize/Greed
    prize_patterns = [
        r'\bwon\b', r'\bprize\b', r'\blottery\b', r'\bclaim\b',
        r'\binheritance\b', r'\bcrypto giveaway\b', r'you(?:\'ve| have) won',
        r'₹\s*\d+[kKmM,]*\s*cash'
    ]
    for pattern in prize_patterns:
        if re.search(pattern, text_lower):
            score += 20
            triggers.append("prize/greed")
            break
            
    # 3. Classic scams & Loan Spam
    scam_patterns = [
        r'\bbank otp\b', r'\bkyc update\b', r'\bfriend in trouble\b', 
        r'\bsend money\b', r'\bwestern union\b', r'\bsuspected fraud\b',
        r'\bpersonal loans?\b', r'\bemergency cash\b', r'\b1st loan free\b',
        r'\bno credit check\b', r'\bapply online\b', r'\bget funds\b'
    ]
    for pattern in scam_patterns:
        if re.search(pattern, text_lower):
            score += 25
            triggers.append("classic scam phrases")
            break
            
    # 4. Caps/punctuation
    if re.search(r'!!!!!+', text):
        score += 10
        triggers.append("excessive punctuation (!!!)")
        
    # Check for excessive ALL CAPS words (simple heuristic: > 5 distinct ALL CAPS words > 3 letters)
    words = re.findall(r'\b[A-Z]{4,}\b', text)
    if len(words) >= 3:
        score += 10
        triggers.append("excessive ALL CAPS")
        
    # Cap score at 100
    score = min(score, 100)
    
    # If it hit multiple severe triggers, boost to 100
    if len(triggers) >= 3 and score < 80:
        score = 85
    
    return {
        "score": score,
        "triggers": triggers
    }
