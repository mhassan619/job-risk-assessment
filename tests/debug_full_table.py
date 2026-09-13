from orchestrator.pipeline import run_pipeline
from data.load_dataset import load_dataset

data = load_dataset()
label_order = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}

rows = []
for entry in data:
    result = run_pipeline(entry["text"], entry.get("email"), entry.get("url"))
    b = result["breakdown"]
    rows.append({
        "id": entry["id"],
        "true": entry["true_label"],
        "predicted": result["risk_level"],
        "total": b["total_diminished"],
        "match": result["risk_level"] == entry["true_label"]
    })

# Sort by true_label severity, then by total score — makes overlaps/conflicts visually obvious
rows.sort(key=lambda r: (label_order[r["true"]], r["total"]))

print(f"{'ID':<6}{'true':<10}{'predicted':<12}{'total':<8}{'match'}")
for r in rows:
    mark = "✅" if r["match"] else "❌"
    print(f"{r['id']:<6}{r['true']:<10}{r['predicted']:<12}{r['total']:<8}{mark}")