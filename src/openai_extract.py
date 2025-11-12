import os
from dotenv import load_dotenv
import openai
from datetime import datetime
# from pydantic import BaseModel

# class Treatment(BaseModel):
#     tratment_line : int
#     treatment_name: str
#     treatment_date: str
#     source_text: str

if __name__ == "__main__":
    # Load API key
    load_dotenv()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    with open("src/txt/prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    with open("src/txt/example_text.txt", "r", encoding="utf-8") as f:
        example_text = f.read()

    user_message = f"{prompt}\n{example_text}"

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "system",
                "content": "Vôce é um hematologista especializado no tratamento do mieloma",
            },
            {"role": "user", "content": open("src/txt/prompt.txt").read()},
            {"role": "user", "content": "Aqui está o texto clínico:"},
            {"role": "user", "content": open("src/txt/example_text.txt").read()},
        ],
        temperature=0.0,
        seed=42,
    )

    reply_text = response.output[0].content[0].text

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"src/results/response_{timestamp}.txt"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(reply_text)

    print(f"Response saved to {output_filename}")
