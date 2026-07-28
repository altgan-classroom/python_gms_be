from datetime import datetime
from typing import Optional, Annotated, Self

from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator, model_validator

from gmsshared.src.util.enums import ReportTypeEnum
from gmsshared.src.util.validators import (
    dictionary_validator,
    date_input_validator,
    check_start_and_end_times,
)


class LocationPath(BaseModel):
    location_id: int = Field(..., description="Location id")


class ReportPath(LocationPath):
    report: ReportTypeEnum = Field(..., description="Type of report.")


class ReportsQuery(BaseModel):
    report_date_from: Annotated[datetime | str | None, BeforeValidator(date_input_validator)] = Field(
        None, description="Date from which create report (inclusive)."
    )

    report_date_to: Annotated[Optional[datetime | str | None], BeforeValidator(date_input_validator)] = Field(
        None, description="Date until which create report (inclusive)."
    )

    filter: Annotated[Optional[dict], BeforeValidator(dictionary_validator)] = Field(
        None, description='Literal filter to apply to the report (i.e. {"key":value})'
    )
    member_id: Optional[int] = Field(None, description="Member id")

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        return check_start_and_end_times(self)
