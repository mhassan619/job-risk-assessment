from orchestrator.pipeline import run_pipeline
from data.load_dataset import load_dataset

data = load_dataset()

for entry in data[:3]:  # pehle 3 cases par test karo, phir sab par
    result = run_pipeline(entry["text"], entry.get("email"), entry.get("url"))

    print(f"\n=== [{entry['id']}] ===")
    if not result["success"]:
        print("VALIDATION FAILED:", result["errors"])
        continue

    print(f"Score: {result['risk_score']} | Level: {result['risk_level']} | Confidence: {result['confidence']}")
    print(f"Degraded: {result['degraded']}")
    print(f"Explanation: {result['explanation']}")
    print(f"Recommendation: {result['recommendation']}")