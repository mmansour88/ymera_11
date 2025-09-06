from fastapi import APIRouter, Body
import random

router = APIRouter()

@router.post("/forecast/montecarlo")
def montecarlo(success_probs: list[float] = Body(...), trials: int = 5000):
    wins = 0
    for _ in range(trials):
        if all(random.random() < p for p in success_probs):
            wins += 1
    return {"estimated_success": wins / trials}
