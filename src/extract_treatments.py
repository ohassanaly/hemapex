import os
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
from openai import OpenAI
import logging

DATE_REGEX = r"^\d{2}/\d{2}/\d{4}$"  # dd/mm/YYYY


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
        except ValueError:
            logging.warning(
                f"Invalid date format received: {v!r} (expected DD/MM/YYYY)"
            )
            return v
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


def extract_treatment_lines(client: OpenAI, note: str) -> TreatmentLines:
    response = client.responses.parse(
        model="gpt-4.1",
        instructions=open("src/txt/instructions.txt").read(),
        input=note,
        text_format=TreatmentLines,
        temperature=0.0,
    )
    return response.output_parsed


if __name__ == "__main__":
    import openai
    from dotenv import load_dotenv
    import pandas as pd
    import json

    load_dotenv()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    treatment_lines = extract_treatment_lines(
        client, Path("src/txt/example_text.txt").read_text()
    )

    try:
        data = treatment_lines.model_dump()
    except AttributeError:
        data = treatment_lines.__dict__

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = f"src/results/response_{timestamp}.csv"
    try:
        pd.DataFrame(data["linhas"]).to_csv(output_path, index=False)
        print(f"Response saved to {output_path}")
    except Exception as e:
        print(e)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = f"src/results/response_{timestamp}.json"
    Path(output_path).write_text(json.dumps(data, indent=2))
    print(f"Response saved to {output_path}")
