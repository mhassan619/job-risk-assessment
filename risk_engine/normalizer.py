def normalize(raw_value: float, max_raw: float) -> float:
    if max_raw <= 0:
        return 0.0
    normalized = (raw_value / max_raw) * 100
    return min(100.0, max(0.0, normalized))