from llm.analyzer import analyze_with_llm
from llm.severity_map import calculate_llm_weight
from data.load_dataset import load_dataset

data = load_dataset()

# Test on one subtle/tricky case first — this is where LLM should add real value
sample = next(d for d in data if d["id"] == "T008")

result = analyze_with_llm(sample["text"], sample.get("email"), sample.get("url"))

print("Contextual flags found:", len(result["contextual_flags"]))
for f in result["contextual_flags"]:
    print(f"  - {f['flag']} ({f['severity']}): {f['reasoning']}")
print("Overall impression:", result["overall_impression"])
print("LLM certainty:", result["llm_certainty"])
print("LLM weight:", calculate_llm_weight(result))