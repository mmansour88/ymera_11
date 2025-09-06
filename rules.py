def auto_flag(metrics: dict) -> str:
    # Simple thresholds: tune as needed
    if metrics.get("security_incidents", 0) > 0: return "red"
    if metrics.get("error_rate", 0) > 0.1: return "orange"
    if metrics.get("latency_ms", 0) > 2000: return "yellow"
    return "green"
