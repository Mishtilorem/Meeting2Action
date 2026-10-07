import re
from datetime import datetime
import dateparser
from rapidfuzz import fuzz, process

def norm(s):
    return " ".join(s.lower().split())

def verify(items, transcript, attendees, meeting_date):
    base = datetime.fromisoformat(str(meeting_date))
    t = norm(transcript)
    out = []
    for it in items:
        quote = norm(it["evidence_quote"])
        flagged, conf = False, it.get("confidence", "medium")

        if quote not in t:
            if fuzz.partial_ratio(quote, t) < 85:
                continue                       # hallucinated, drop it
            flagged, conf = True, "low"        # close but not exact

        owner = it.get("owner")
        if owner and attendees:
            m = process.extractOne(owner, attendees, scorer=fuzz.WRatio, score_cutoff=80)
            if m:
                owner = m[0]
            else:
                flagged = True                 # owner isn't a known attendee

        due = None
        if it.get("due_text"):
            raw_due = it["due_text"].strip()
            # Clean common prepositions and relative prefixes like 'by', 'before', 'on', 'due', 'next'
            clean_due = re.sub(r'^(by|before|on|due|until)\s+', '', raw_due, flags=re.IGNORECASE)
            d = dateparser.parse(clean_due, settings={"RELATIVE_BASE": base, "PREFER_DATES_FROM": "future"})
            if not d:
                clean_due_no_next = re.sub(r'^next\s+', '', clean_due, flags=re.IGNORECASE)
                d = dateparser.parse(clean_due_no_next, settings={"RELATIVE_BASE": base, "PREFER_DATES_FROM": "future"})
            if not d:
                d = dateparser.parse(raw_due, settings={"RELATIVE_BASE": base, "PREFER_DATES_FROM": "future"})
            due = d.date().isoformat() if d else None

        out.append({**it, "owner": owner, "due_date": due, "flagged": flagged, "confidence": conf})
    return out
