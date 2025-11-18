from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import logging

DATE_REGEX = r"^\d{2}/\d{2}/(\d{2}|\d{4})$"  # dd/mm/YYYY or dd/mm/YY


class TreatmentLine(BaseModel):
    line_number: int = Field(
        ..., description="Número da linha de tratamento oncologico"
    )

    inducao_start: Optional[str] = Field(
        None, pattern=DATE_REGEX, description="Data de início da indução"
    )
    inducao_end: Optional[str] = Field(
        None, pattern=DATE_REGEX, description="Data de término da indução"
    )
    inducao_medicamentos: Optional[str] = Field(
        None,
        description="Medicamentos utilizados durante a terapia de indução. "
        "Pode ser VCd (Bortezomibe + Ciclofosfamida + Dexametasona) "
        "ou VRd (Bortezomibe + Lenalidomida + Dexametasona) "
        "ou VTD (Bortezomibe + Talidomida + Dexametasona) "
        "ou Dara-VRd  (Daratumumabe + VRd) "
        "ou Outros",
    )

    consolidacao_start: Optional[str] = Field(
        None, pattern=DATE_REGEX, description="Data de início da consolidação"
    )
    consolidacao_end: Optional[str] = Field(
        None, pattern=DATE_REGEX, description="Data de término da consolidação"
    )
    consolidacao_medicamentos: Optional[str] = Field(
        None,
        description="Medicamentos utilizados durante a terapia de consolidação. VRd ou VCd",
    )

    manutencao_start: Optional[str] = Field(
        None, pattern=DATE_REGEX, description="Data de início da manutenção"
    )
    manutencao_end: Optional[str] = Field(
        None, pattern=DATE_REGEX, description="Data de término da manutenção"
    )
    manutencao_medicamentos: Optional[str] = Field(
        None,
        description="Medicamentos utilizados durante a terapia de manutenção. Talidomida ou Lenalidomida ou Bortezomibe ou Ixazomibe ou Outros",
    )

    radio_start: Optional[str] = Field(
        None, pattern=DATE_REGEX, description="Data de início da radioterapia"
    )
    radio_end: Optional[str] = Field(
        None, pattern=DATE_REGEX, description="Data de término da radioterapia"
    )

    transplant_dt: Optional[str] = Field(
        None, pattern=DATE_REGEX, description="Data do transplante"
    )

    transplant_type: Optional[str] = Field(
        None, description="Tipo de transplante: 'autologo' ou 'alogenico'"
    )

    # Extra safety: enforce dd/mm/YYYY via Python as well
    @field_validator(
        "inducao_start",
        "inducao_end",
        "consolidacao_start",
        "consolidacao_end",
        "manutencao_start",
        "manutencao_end",
        "radio_start",
        "radio_end",
        "transplant_dt",
        mode="before",
    )
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
            corrected = dt.strftime("%d/%m/%Y")
            logging.warning(f"Corrected MM/DD/YY to DD/MM/YYYY: {v!r} -> {corrected!r}")
            return corrected
        except ValueError:
            pass

        logging.warning(
            f"Invalid date format received: {v!r} (expected DD/MM/YYYY or a convertible variant)"
        )
        return v

    @field_validator("transplant_type", mode="before")
    def normalize_transplant_type(cls, v):
        if v is None:
            return v
        v = v.lower().strip()
        if v in {"autologo", "autólogo"}:
            return "autologo"
        if v in {"alogênico", "alogenico", "alogênico"}:
            return "alogenico"
        logging.warning(f"Invalid transplant type : {v}")
        return v


class TreatmentLines(BaseModel):
    linhas: List[TreatmentLine]
