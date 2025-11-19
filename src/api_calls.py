"""
Implementing the different API calls for structured outputs
"""

from enum import Enum
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
import json

T = TypeVar("T", bound=BaseModel)


class Provider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    MISTRAL = "mistral"
    GROQ = "groq"


MODELS = {
    Provider.OPENAI: "gpt-4.1",
    Provider.GEMINI: "gemini-2.5-pro",
    Provider.MISTRAL: "open-mistral-7b",  # free tier
    Provider.GROQ: "moonshotai/kimi-k2-instruct-0905",  # https://console.groq.com/docs/structured-outputs#supported-models
}


def wrap_result(result):
    """
    Ensure the result is a str so it can feed model_validate_json
    input : result as the API output
    returns : stringified result
    """
    if isinstance(result, str):
        return result
    elif isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)
    else:
        raise TypeError(f"Don't know how to handle type {type(result)}")


def call_llm_structured(
    provider: Provider,
    model: str,
    instruction: str,
    unstructured_text: str,
    schema_model: Type[T],
) -> T:
    if provider == Provider.OPENAI:
        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
        import os

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model=model,
            contents=("\n").join([instruction, unstructured_text]),
            config={
                "response_mime_type": "application/json",
                "response_schema": schema_model.model_json_schema(),
            },
        )
        return schema_model.model_validate_json(response.text)

    elif provider == Provider.MISTRAL:
        from mistralai import Mistral
        import os

        client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

        system_msg = ("\n").join(
            [
                instruction,
                "You MUST produce JSON that matches this schema exactly :",
                json.dumps(schema_model.model_json_schema()),
            ]
        )

        response = client.chat.complete(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": unstructured_text},
            ],
            response_format={
                "type": "json_object",
            },
        )

        try:
            result = wrap_result(response.choices[0].message.content)
        except Exception as e:
            print("could not infer type of the result", e)
            return
        try:
            return schema_model.model_validate_json(result)
        except ValidationError as e:
            print(e)
            return result
        except Exception:
            return

    elif provider == Provider.GROQ:
        from groq import Groq
        import os

        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

        system_msg = ("\n").join(
            [
                instruction,
                "You MUST produce JSON that matches this schema exactly :",
                json.dumps(schema_model.model_json_schema()),
            ]
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": unstructured_text},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "product_review",
                    "schema": schema_model.model_json_schema(),
                },
            },
        )

        try:
            result = wrap_result(response.choices[0].message.content)
        except Exception as e:
            print("could not infer type of the result", e)
            return
        try:
            return schema_model.model_validate_json(result)
        except ValidationError as e:
            print(e)
            return result
        except Exception:
            return

    else:
        raise ValueError(f"Unknown provider: {provider}")


if __name__ == "__main__":
    from structured_treatment import TreatmentLines
    from datetime import datetime
    from pathlib import Path
    from dotenv import load_dotenv
    import json

    # test providers one by one
    for provider in Provider:
        print("___")
        print(provider.value)
        print("___")
        model = MODELS[provider]

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = (
            Path(".") / f"src/results/testing/{timestamp}_{model.replace('/', '')}.json"
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
        except Exception:
            try:
                Path(output_path).write_text(json.dumps(result, indent=2))
                print("JSON validation failed ; saving the dict result")
                print(f"Response saved to {output_path}")
            except Exception as e:
                print(e)
