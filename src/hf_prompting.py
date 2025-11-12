from transformers import pipeline
from pydantic import BaseModel, ValidationError
import json
import re


# --- Define your structured schema ---
class Treatment(BaseModel):
    treatment_name: str
    treatment_date: str
    source_text: str


# --- Load a Hugging Face model ---
pipe = pipeline("text-generation", model="pucpr-br/Clinical-BR-LlaMA-2-7B")


# --- Define a parsing helper (like responses.parse) ---
def hf_parse(model_pipeline, prompt: str, response_format: BaseModel):
    system_prompt = f"""
You are a structured data extraction assistant specialized in myeloma care.
Return the output as valid JSON matching this schema:
{response_format.model_json_schema()}
---
{prompt}
"""
    output = model_pipeline(system_prompt, max_new_tokens=300, temperature=0.1)
    text = output[0]["generated_text"]

    # Try to extract JSON
    try:
        json_str = re.search(r"\{.*\}", text, re.DOTALL).group(0)
        parsed = json.loads(json_str)
        return response_format(**parsed)
    except (json.JSONDecodeError, ValidationError, AttributeError) as e:
        return {"error": str(e), "raw_output": text}


# --- Example usage ---
prompt = "Given this haematology clinical note, provide for each oncological treatment you identify : the name of the treatment, its dates and cite the part of the text used"
result = hf_parse(pipe, prompt, Treatment)

print(result)
