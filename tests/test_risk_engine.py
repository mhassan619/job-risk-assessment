from data.load_dataset import load_dataset
from rules.rule_engine import run_all_rules
from llm.analyzer import analyze_with_llm
from verification.verifier import run_verification
from risk_engine.scorer import calculate_risk

data = load_dataset()

for entry in data:
    rule_result = run_all_rules(entry["text"], email=entry.get("email"))
    llm_result = analyze_with_llm(entry["text"], entry.get("email"), entry.get("url"))
    verification_result = run_verification(entry["text"], entry.get("email"), entry.get("url"))

    risk = calculate_risk(rule_result, llm_result, verification_result)

    match = "✅" if risk["risk_level"] == entry["true_label"] else "❌"
    print(f"{match} [{entry['id']}] predicted={risk['risk_level']} ({risk['final_score']}) "
          f"| true={entry['true_label']} | confidence={risk['confidence']}")