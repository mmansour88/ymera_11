
def combine_scores(metrics: dict) -> float:
    # Weighted scoring; tune weights later
    w = {"quality":0.5,"speed":0.3,"cost":0.2}
    return sum(metrics[k]*w.get(k,0) for k in metrics if k in w)
