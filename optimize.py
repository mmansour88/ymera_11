from fastapi import APIRouter, Body
import random, math

router = APIRouter()

@router.post("/optimize/assign")
def assign(tasks: list[dict] = Body(...), workers: list[dict] = Body(...)):
    result = []
    for t in tasks:
        best = max(workers, key=lambda w: w.get("skills",{}).get(t["type"],0))
        result.append({"task": t["id"], "worker": best["id"]})
    return {"assignments": result}

@router.post("/optimize/anneal")
def anneal(costs: list[list[float]] = Body(...), steps: int = 1000):
    n = len(costs)
    perm = list(range(n))
    best = perm[:]; best_cost = sum(costs[i][perm[i]] for i in range(n))
    T = 1.0
    import random as _r, math as _m
    for _ in range(steps):
        i,j = _r.randrange(n), _r.randrange(n)
        perm[i], perm[j] = perm[j], perm[i]
        c = sum(costs[k][perm[k]] for k in range(n))
        if c < best_cost or _r.random() < _m.exp((best_cost - c)/max(1e-6,T)):
            best, best_cost = perm[:], c
        else:
            perm[i], perm[j] = perm[j], perm[i]
        T *= 0.999
    return {"perm": best, "cost": best_cost}
