from orchestrator.pipeline import run_pipeline
from data.load_dataset import load_dataset

data = load_dataset()
correct = 0
results_log = []

for i, entry in enumerate(data):
    # Defensive check: catch a malformed entry immediately with full context,
    # instead of a bare KeyError that doesn't say which entry or why
    if "text" not in entry:
        print(f"[SKIPPED] Entry at index {i} is missing 'text'. Full entry: {entry}")
        continue

    result = run_pipeline(entry["text"], entry.get("email"), entry.get("url"))

    if not result["success"]:
        print(f"[{entry.get('id', f'index_{i}')}] SKIPPED (validation failed): {result['errors']}")
        continue

    predicted = result["risk_level"]
    actual = entry.get("true_label", "UNKNOWN")
    is_match = predicted == actual
    correct += is_match

    results_log.append({
        "id": entry.get("id", f"index_{i}"),
        "type": entry.get("type", "unknown"),
        "predicted": predicted,
        "actual": actual,
        "score": result["risk_score"],
        "match": is_match
    })

    status = "✅" if is_match else "❌"
    print(f"{status} [{entry.get('id')}] ({entry.get('type')}) predicted={predicted} actual={actual} score={result['risk_score']}")

total = len(results_log)
if total > 0:
    print(f"\nAccuracy: {correct}/{total} ({round(correct/total*100, 1)}%)")
else:
    print("\nNo valid entries were evaluated.")

mismatches = [r for r in results_log if not r["match"]]
if mismatches:
    print("\nMismatches by type:")
    for m in mismatches:
        print(f"  - [{m['id']}] {m['type']}: predicted {m['predicted']}, expected {m['actual']}")