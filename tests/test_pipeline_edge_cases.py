from orchestrator.pipeline import run_pipeline

# Empty text
print(run_pipeline(""))

# Too short
print(run_pipeline("hi"))

# No email/url at all
print(run_pipeline("We are hiring a software developer for our growing team with great benefits."))