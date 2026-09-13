from rules.rule_engine import run_all_rules

sample_text = """
URGENT HIRING! Earn $5000 weekly, no experience needed high pay.
Pay a registration fee of $50 to confirm your seat. Contact us on WhatsApp only.
"""

result = run_all_rules(sample_text, email="recruiter123@gmail.com")

print("Triggered rules:", result["rule_count"])
for r in result["triggered_rules"]:
    print(f"  [{r['id']}] {r['description']} (weight: {r['weight']})")
print("Total rule weight:", result["total_rule_weight"])