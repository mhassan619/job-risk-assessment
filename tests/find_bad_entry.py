import json

with open("data/test_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total entries loaded: {len(data)}\n")

for i, entry in enumerate(data):
    missing = [k for k in ["id", "type", "text", "true_label"] if k not in entry]
    if missing:
        print(f"Entry #{i} (id={entry.get('id', 'UNKNOWN')}) is MISSING keys: {missing}")
        print(f"  Full entry: {entry}\n")

print("Check complete.")