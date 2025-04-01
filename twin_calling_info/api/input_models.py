from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

phone_number_pattern = r"^7\d{1,14}$"


class InputCallEnd(BaseModel):
    model_config = ConfigDict(extra="allow")

    callTo: str | None = Field(pattern=phone_number_pattern, default=None)
    event: str | None = Field(default=None)
    startedAt: datetime | None = Field(default=None)
    finishedAt: datetime | None = Field(default=None)
    status: str | None = Field(default=None)

    @field_validator("*", mode="before")
    @classmethod
    def validate_input(cls, v):
        if v == "":
            return None
        return v
