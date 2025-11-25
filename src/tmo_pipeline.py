from api_calls import Provider, MODELS, call_llm_structured
from pathlib import Path

test_mode = False
erase_mode = False
n_test = 2
tasy_src_path = Path(".") / "src/data/tasy_api.csv"

provider = Provider.OPENAI
model = MODELS[provider]
single_dir = Path(".") / f"src/results/tmo_{provider.value}_rghc/"
global_dir = Path(".") / f"src/results/tmo_{provider.value}_full_result/"

single_dir.mkdir(parents=True, exist_ok=True)
global_dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    from structured_relapse import Relapse
    from datetime import datetime

    from dotenv import load_dotenv
    import pandas as pd
    from tqdm import tqdm

    import logging
    import json

    load_dotenv()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = Path(".") / f"src/logs/tmo_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=log_path,
        filemode="a",
    )

    load_dotenv()
    text_df = pd.read_csv(tasy_src_path)

    if test_mode:
        api_df = text_df.iloc[:n_test][["rghc", "text"]]
        logging.info(f"Extracting treatments for {api_df.rghc.nunique()} rghc")
    else:
        api_df = text_df[["rghc", "text"]]
        logging.info(f"Extracting treatments for {api_df.rghc.nunique()} rghc")

    full_data = {}

    for index, row in tqdm(api_df.iterrows()):
        rghc = row["rghc"]
        logging.info(f"Processing rghc : {rghc}")
        single_output_path = single_dir / f"{rghc}.json"
        # check if the patient was already processed
        if not erase_mode and single_output_path.exists():
            logging.info(f"Patient {rghc} already processed")
            continue

        else:
            result = call_llm_structured(
                provider=provider,
                model=model,
                instruction=open(Path(".") / "src/txt/tmo_instructions.txt").read(),
                unstructured_text=row["text"],
                schema_model=Relapse,
            )

            try:
                data = result.model_dump()
            except Exception as e:
                print(f"Failed to save response for {provider.value}: {e}")

            try:
                full_data[rghc] = data
                # save results one by one for safety
                with open(single_output_path, "w") as f:
                    json.dump(data, f, indent=4)
                logging.info(f"Response for {rghc} saved to {single_output_path}")
            except Exception as e:
                logging.error(e)

    # final save
    try:
        global_output_path = global_dir / f"tmo_rghc_{timestamp}.csv"
        with open(global_output_path, "w") as f:
            json.dump(full_data, f, indent=4)
        logging.info(f"Full extraction saved to {global_output_path}")
    except Exception as e:
        logging.error(e)
