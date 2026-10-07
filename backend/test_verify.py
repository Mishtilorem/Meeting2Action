from datetime import date
from verify import verify

transcript = "Priya: I will send the Q3 report to Rahul by next Friday."
attendees = ["Priya", "Rahul", "Alex"]
meeting_date = date(2026, 10, 7)

test_items = [
    {
        "task": "Send Q3 report",
        "owner": "Priya",
        "due_text": "by next Friday",
        "evidence_quote": "I will send the Q3 report to Rahul by next Friday.",
        "confidence": "high"
    },
    {
        "task": "Invented task not in transcript",
        "owner": "Sarah",
        "due_text": "tomorrow",
        "evidence_quote": "Sarah will build a rocket ship by tomorrow.",
        "confidence": "high"
    }
]

if __name__ == "__main__":
    verified = verify(test_items, transcript, attendees, meeting_date)
    print("Verification Results:")
    print(verified)
    assert len(verified) == 1, f"Expected 1 valid item after dropping hallucinated item, got {len(verified)}"
    assert verified[0]["due_date"] is not None, "Expected parsed due_date"
    print("Verification test passed successfully!")
