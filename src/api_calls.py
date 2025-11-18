"""
Implementing the different API calls for structured outputs
"""

from enum import Enum
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class Provider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    MISTRAL = "mistral"


def call_llm_structured(
    provider: Provider,
    model: str,
    instruction: str,
    unstructured_text: str,
    schema_model: Type[T],
) -> T:
    if provider == Provider.OPENAI:
        from openai import OpenAI

        client = OpenAI()
        response = client.responses.parse(
            model=model,
            instructions=instruction,
            input=unstructured_text,
            text_format=schema_model,
            temperature=0.0,
        )
        return response.output_parsed

    elif provider == Provider.GEMINI:
        from google import genai

        client = genai.Client()
        response = client.models.generate_content(
            model=model,
            contents=("\n").join([instruction, unstructured_text]),
            config={
                "response_mime_type": "application/json",
                "response_schema": schema_model.model_json_schema(),
            },
        )
        return schema_model.model_validate_json(response.text)

    else:
        raise ValueError(f"Unknown provider: {provider}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    from structured_treatment import TreatmentLines
    from datetime import datetime
    from pathlib import Path
    import json

    # provider = Provider.OPENAI
    # model = "gpt-4.1"
    provider = Provider.GEMINI
    model = "gemini-2.5-pro"

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = (
        Path(".") / f"src/results/testing/{provider.value}_{model}_{timestamp}.json"
    )

    load_dotenv()
    result = call_llm_structured(
        provider=provider,
        model=model,
        instruction=open("src/txt/instructions.txt").read(),
        unstructured_text=open("src/txt/example_text.txt").read(),
        schema_model=TreatmentLines,
    )
    try:
        data = result.model_dump()
        Path(output_path).write_text(json.dumps(data, indent=2))
        print(f"Response saved to {output_path}")
    except AttributeError:
        data = result.__dict__
