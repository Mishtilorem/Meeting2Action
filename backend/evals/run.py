import os, json, glob
from dotenv import load_dotenv
load_dotenv()

from rapidfuzz import fuzz
from llm import Budget
from extraction import extract
from verify import verify

def evaluate():
    cases_dir = os.path.join(os.path.dirname(__file__), "cases")
    cases = glob.glob(os.path.join(cases_dir, "*.json"))
    if not cases:
        print("No evaluation cases found in evals/cases/")
        return

    tp, fp, fn = 0, 0, 0
    for case_file in cases:
        with open(case_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        budget = Budget(60000)
        ext = extract(data["transcript"], budget)
        items = [i.model_dump() for i in ext.action_items]
        verified = verify(items, data["transcript"], data.get("attendees", []), data.get("meeting_date", "2026-10-07"))

        expected = data.get("expected_action_items", [])
        
        matched_expected = set()
        for v in verified:
            match = False
            for idx, exp in enumerate(expected):
                if fuzz.token_set_ratio(v["task"], exp["task"]) > 75:
                    match = True
                    matched_expected.add(idx)
                    break
            if match:
                tp += 1
            else:
                fp += 1

        fn += (len(expected) - len(matched_expected))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    print("=== EVALUATION SUITE RESULTS ===")
    print(f"True Positives (TP) : {tp}")
    print(f"False Positives (FP): {fp}")
    print(f"False Negatives (FN): {fn}")
    print(f"Precision          : {precision * 100:.2f}%")
    print(f"Recall             : {recall * 100:.2f}%")
    print(f"F1 Score           : {f1 * 100:.2f}%")

if __name__ == "__main__":
    evaluate()
