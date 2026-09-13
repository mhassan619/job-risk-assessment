def safe_run(component_name: str, func, *args, fallback: dict, **kwargs) -> dict:
    """
    Runs a pipeline component safely. If it fails, logs the failure and
    returns a fallback so the rest of the pipeline can still proceed.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"[WARNING] {component_name} failed: {e}")
        result = dict(fallback)
        result["_component_failed"] = True
        result["_error"] = str(e)
        return result