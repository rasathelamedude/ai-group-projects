from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.calculate_combination import calculate_combination
from backend.build_binomial_table import build_binomial_table
from backend.validation import validate_team_inputs


class CalculationRequest(BaseModel):
    total_developers: str
    team_size: str


class CalculationResponse(BaseModel):
    total_developers: int
    team_size: int
    total_teams: int
    table: list[list[int]]


app = FastAPI(title="Forming Project Teams API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/calculate", response_model=CalculationResponse)
def calculate_team_count(payload: CalculationRequest) -> CalculationResponse:
    try:
        total_developers, team_size = validate_team_inputs(
            payload.total_developers,
            payload.team_size,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    total_teams = calculate_combination(total_developers, team_size)
    table = build_binomial_table(total_developers)

    return CalculationResponse(
        total_developers=total_developers,
        team_size=team_size,
        total_teams=total_teams,
        table=table,
    )
