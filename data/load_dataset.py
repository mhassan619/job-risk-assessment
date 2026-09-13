import json
import os

VALID_LABELS = {"Low", "Medium", "High", "Critical"}

def load_dataset(path="data/test_dataset.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def validate_dataset(data):
    """Sanity checks before using dataset for testing."""
    errors = []
    seen_ids = set()

    for entry in data:
        if entry["id"] in seen_ids:
            errors.append(f"Duplicate ID: {entry['id']}")
        seen_ids.add(entry["id"])

        if entry["true_label"] not in VALID_LABELS:
            errors.append(f"{entry['id']}: invalid label '{entry['true_label']}'")

        if len(entry["text"].strip()) < 20:
            errors.append(f"{entry['id']}: text too short, looks incomplete")

    return errors

if __name__ == "__main__":
    data = load_dataset()
    print(f"Loaded {len(data)} entries")

    errors = validate_dataset(data)
    if errors:
        print("Issues found:")
        for e in errors:
            print(" -", e)
    else:
        print("Dataset validated successfully, no issues found.")