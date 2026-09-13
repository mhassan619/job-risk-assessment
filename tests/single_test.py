from orchestrator.pipeline import run_pipeline
from data.load_dataset import load_dataset

data = load_dataset()
targets = ["T008", "T009"]

for entry in data:
    if entry["id"] in targets:
        result = run_pipeline(entry["text"], entry.get("email"), entry.get("url"))
        print(f"[{entry['id']}] {result.get('risk_level')} ({result.get('risk_score')}) | degraded={result.get('degraded')}")