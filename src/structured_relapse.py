from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import logging

DATE_REGEX = r"^\d{2}/\d{2}/(\d{2}|\d{4})$"  # dd/mm/YYYY or dd/mm/YY


class Relapse(BaseModel):
    relapse: bool = Field(
        ..., description="O paciente teve uma recaída após o transplante."
    )

    relapse_dt: Optional[str] = Field(
        None, pattern=DATE_REGEX, description="data da recidiva pós-transplante"
    )

    # Extra safety: enforce dd/mm/YYYY via Python as well
    @field_validator("relapse_dt")
    def validate_date(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%d/%m/%Y")
            return v
        except ValueError:
            pass

        try:
            dt = datetime.strptime(v, "%m/%d/%Y")
            corrected_dt = dt.strftime("%d/%m/%Y")
            logging.warning(
                f"Corrected date from MM/DD/YYYY to DD/MM/YYYY: {v!r} -> {corrected_dt!r}"
            )
            return corrected_dt
        except ValueError:
            pass

        try:
            dt = datetime.strptime(
                v, "%d/%m/%y"
            )  # "00"–"68" → years 2000–2068 ; "69"–"99" → years 1969–1999
            corrected_dt = dt.strftime("%d/%m/%Y")
            logging.warning(
                f"Corrected date from DD/MM/YY to DD/MM/YYYY: {v!r} -> {corrected_dt!r}"
            )
            return corrected_dt
        except ValueError:
            pass

        try:
            dt = datetime.strptime(v, "%m/%d/%y")
            corrected_dt = dt.strftime("%d/%m/%Y")
            logging.warning(
                f"Corrected MM/DD/YY to DD/MM/YYYY: {v!r} -> {corrected_dt!r}"
            )
            return corrected_dt
        except ValueError:
            pass

        try:
            dt = datetime.strptime(v, "%m/%Y")
            corrected_dt = dt.replace(day=15).strftime("%d/%m/%Y")
            logging.warning(
                f"Corrected MM/YY to DD/MM/YYYY (mid of the month): {v!r} -> {corrected_dt!r}"
            )
            return corrected_dt
        except ValueError:
            pass

        logging.warning(
            f"Invalid date format received: {v!r} (expected DD/MM/YYYY or a convertible variant)"
        )
        return v
