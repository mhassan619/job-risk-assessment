from orchestrator.pipeline import run_pipeline
from data.load_dataset import load_dataset

data = load_dataset()
targets = ["T005", "T031", "T032", "T033", "T034", "T036", "T037",
           "T039", "T045", "T047", "T048", "T050"]

for entry in data:
    if entry["id"] in targets:
        result = run_pipeline(entry["text"], entry.get("email"), entry.get("url"))
        print(f"\n=== [{entry['id']}] true={entry['true_label']} predicted={result['risk_level']} ({result['risk_score']}) ===")
        print("Rule flags:")
        if result["rule_flags"]:
            for r in result["rule_flags"]:
                print(f"  - [{r['id']}] {r['description']}")
        else:
            print("  (none)")
        print("LLM flags:")
        for f in result["llm_flags"]:
            print(f"  - {f['flag']} ({f.get('severity','?')})")