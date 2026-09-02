from pydantic import BaseModel, Field
from typing import List


class AdvisoryRequest(BaseModel):
    age_group: str = Field(
        ...,
        description="Age group of the citizen"
    )

    health_conditions: List[str] = Field(
        default_factory=list,
        description="List of existing health conditions"
    )

    activity_level: str = Field(
        ...,
        description="Planned activity level"
    )

    latitude: float = Field(
        ...,
        description="Citizen latitude obtained from device location"
    )

    longitude: float = Field(
        ...,
        description="Citizen longitude obtained from device location"
    )