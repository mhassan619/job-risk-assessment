from data.load_dataset import load_dataset
from verification.verifier import run_verification

data = load_dataset()

for entry in data:
    result = run_verification(entry["text"], entry.get("email"), entry.get("url"))
    print(f"[{entry['id']}] true_label={entry['true_label']} | verification_weight={result['total_verification_weight']}")
    for f in result["verification_flags"]:
        print(f"    - {f['description']} (weight: {f['weight']})")