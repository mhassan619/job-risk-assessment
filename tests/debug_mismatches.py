from orchestrator.pipeline import run_pipeline
from data.load_dataset import load_dataset

data = load_dataset()
targets = ["T005", "T006", "T008"]

for entry in data:
    if entry["id"] in targets:
        result = run_pipeline(entry["text"], entry.get("email"), entry.get("url"))
        b = result["breakdown"]
        print(f"\n=== [{entry['id']}] true={entry['true_label']} predicted={result['risk_level']} ({result['risk_score']}) ===")
        print(f"rule={b['rule_diminished']} | llm={b['llm_diminished']} | verification={b['verification_diminished']} | total={b['total_diminished']}")
        print("LLM flags:")
        for f in result["llm_flags"]:
            print(f"  - {f['flag']} ({f.get('severity','?')})")