from orchestrator.pipeline import run_pipeline
from data.load_dataset import load_dataset

data = load_dataset()

print(f"{'ID':<6}{'true':<10}{'rule':<9}{'llm':<9}{'veri':<9}{'total':<9}")
for entry in data:
    result = run_pipeline(entry["text"], entry.get("email"), entry.get("url"))
    b = result["breakdown"]
    print(f"{entry['id']:<6}{entry['true_label']:<10}{b['rule_diminished']:<9}{b['llm_diminished']:<9}{b['verification_diminished']:<9}{b['total_diminished']:<9}")