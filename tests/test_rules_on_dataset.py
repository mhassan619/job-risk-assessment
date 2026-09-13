from data.load_dataset import load_dataset
from rules.rule_engine import run_all_rules

data = load_dataset()

for entry in data:
    result = run_all_rules(entry["text"], email=entry.get("email"))
    print(f"[{entry['id']}] true_label={entry['true_label']} | rules_triggered={result['rule_count']} | weight={result['total_rule_weight']}")