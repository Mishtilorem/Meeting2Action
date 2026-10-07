from rapidfuzz import fuzz
from llm import chat_json, FAST, SMART
from models import Extraction

SYSTEM = """You extract outcomes from meeting transcripts.
Only include action items that were explicitly committed to.
evidence_quote must be copied EXACTLY from the text. owner is a person's name or null.
due_text is the raw phrase (e.g. 'by Friday') or null. Never invent anything."""

def chunk_text(text, size=6000, overlap=600):
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i + size])
        i += size - overlap
    return chunks

def is_dup(a, b):
    if a.evidence_quote.strip() == b.evidence_quote.strip():
        return True
    same_owner = (a.owner or "").lower() == (b.owner or "").lower()
    return same_owner and fuzz.token_set_ratio(a.task, b.task) > 85

def extract(transcript, budget):
    parts = [chat_json(Extraction, SYSTEM, ch, FAST, budget) for ch in chunk_text(transcript)]

    items = []
    for p in parts:
        for it in p.action_items:
            if not any(is_dup(it, o) for o in items):
                items.append(it)
    merged = Extraction(
        decisions=list(dict.fromkeys(d for p in parts for d in p.decisions)),
        action_items=items,
        open_questions=list(dict.fromkeys(q for p in parts for q in p.open_questions)),
    )
    if len(items) > 1:  # final cleanup pass catches paraphrased duplicates
        merged = chat_json(
            Extraction,
            "Merge duplicate or overlapping action items in this JSON. Keep each evidence_quote "
            "unchanged. Do not add new items.",
            merged.model_dump_json(), SMART, budget)
    return merged
