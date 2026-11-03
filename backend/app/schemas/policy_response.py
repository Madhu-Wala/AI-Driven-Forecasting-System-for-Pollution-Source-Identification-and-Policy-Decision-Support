from typing import Any, Literal

from pydantic import BaseModel, Field


class StationSummary(BaseModel):
    station_id: str
    station_name: str
    aqi: float | None = None
    aqi_category: str | None = None


class SourceAssessment(BaseModel):
    source: str
    score: float | None = None
    signal: Literal["positive", "negative", "neutral", "unknown"]
    interpretation: str


class ExpectedImpact(BaseModel):
    description: str
    quantitative_estimate_available: bool = False
    quantitative_estimate: float | None = None
    reason: str | None = None


class PolicyRecommendation(BaseModel):
    recommendation_id: str
    title: str
    intervention: str
    rationale: str
    priority: Literal["high", "medium", "low"]
    responsible_authority: str
    implementation_conditions: list[str] = Field(default_factory=list)
    expected_impact: ExpectedImpact
    evidence_ids: list[str] = Field(default_factory=list)


class SimulationInput(BaseModel):
    recommendation_id: str
    intervention_type: str
    selected: bool = False
    parameters: dict[str, Any] = Field(default_factory=dict)
    quantitative_effect_available: bool = False
    limitation: str


class PolicyEvidence(BaseModel):
    evidence_id: str
    source: str
    category: str
    file_name: str


class PolicyGenerationResponse(BaseModel):
    station_summary: StationSummary
    source_assessment: list[SourceAssessment]
    recommendations: list[PolicyRecommendation]
    simulation_inputs: list[SimulationInput]
    evidence: list[PolicyEvidence]
    limitations: list[str] = Field(default_factory=list)